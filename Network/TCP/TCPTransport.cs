using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using Wave.Common;
using Wave.Platform.Messaging;
using Wave.Services;

namespace Wave.Network
{
    public class TCPTransport : TransportBase
    {
        public const int TCPSessionHeaderSize = 8;

        private AsyncQueue<byte[]> outbox = new AsyncQueue<byte[]>();
        private TCPInput input = null;

        private TCPSocket socket = null;
        private DnsEndPoint endPoint = null;
        private int portOverride = -1;

        private byte[] sessionID = null;
        private bool isFirstSend = true;
        private bool isFirstReceive = true;

        public TCPTransport(NetworkAgent.INetworkAgentControl ctrl)
            : base(ctrl)
        {
        }

        public override void Open()
        {
            if (State == TransportState.Uninitialised)
            {
                // verify current application
                if (!Core.Application.HasTCP)
                {
                    OnError(TransportErrorCode.NoConnectionData);
                    return;
                }

                // creating default session ID
                if (sessionID == null)
                {
                    sessionID = new byte[TCPSessionHeaderSize];
                    sessionID[0] = 6;
                }

                // creating input processor
                if (input == null)
                    input = new TCPInput();

                // creating socket
                if (endPoint == null)
                {
                    DebugHelper.Out(
                        "Creating TCP endpoint to host {0} and port {1}",
                        Core.Application.TCP.Host,
                        (portOverride != -1) ? portOverride : Core.Application.TCP.Port);

                    endPoint = new DnsEndPoint(Core.Application.TCP.Host, (portOverride != -1) ? portOverride : Core.Application.TCP.Port);
                }

                Connect();
            }
        }

        public override void Connect()
        {
            if (State != TransportState.Connected)
            {
                State = TransportState.Connecting;

                if (socket == null)
                {
                    socket = new TCPSocket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

                    socket.Connected += new EventHandler<SocketAsyncEventArgs>(socket_Connected);
                    socket.Sent += new EventHandler<SocketAsyncEventArgs>(socket_Sent);
                    socket.Received += new EventHandler<SocketAsyncEventArgs>(socket_Received);
                }

                socket.Connect(endPoint);
            }
        }

        private void socket_Connected(object sender, SocketAsyncEventArgs e)
        {
            ThreadHelper.Sync(() =>
            {
                if (e.SocketError == SocketError.Success)
                {
                    State = TransportState.Connected;

                    StartSend();
                }
                else
                {
                    State = TransportState.Disconnected;

                    OnError(TransportErrorCode.LostConnection);
                }

                e.Dispose();
            });
        }

        private void StartSend()
        {
            if (State == TransportState.Connected)
            {
                // prepare data to send (if any)
                byte[] data = null;

                if (outbox.CanDequeue)
                {
                    byte[] temp = outbox.BeginDequeue();

                    if (temp != null)
                    {
                        using (MemoryStream mem = new MemoryStream())
                        {
                            // session ID
                            if (isFirstSend)
                            {
                                isFirstSend = false;
                                mem.WriteBytes(sessionID);
                            }

                            // payload size
                            mem.WriteShort((short)(temp.Length + PriorityHeaderSize));

                            // if encrypting, we need another stream
                            if (Core.Network.TransactionalEncryption != null)
                            {
                                byte[] toEncode = null;

                                using (MemoryStream enc = new MemoryStream())
                                {
                                    // priority header (always priority 3 -> highest transactional one)
                                    int msgLength = temp.Length;
                                    enc.WriteByte((byte)((3 & 0x0F) | (((msgLength) & 0x000F) << 4)));
                                    enc.WriteByte((byte)(msgLength >> 4));

                                    // data
                                    enc.WriteBytes(temp);

                                    // encrypt
                                    toEncode = enc.ToArray();
                                    Core.Network.TransactionalEncryption.Encrypt(toEncode, toEncode.Length);
                                }

                                // writing encoded data
                                if (toEncode != null)
                                    mem.WriteBytes(toEncode);
                            }
                            else
                            {
                                // priority header (always priority 3 -> highest transactional one)
                                int msgLength = temp.Length;
                                mem.WriteByte((byte)((3 & 0x0F) | (((msgLength) & 0x000F) << 4)));
                                mem.WriteByte((byte)(msgLength >> 4));

                                // data
                                mem.WriteBytes(temp);
                            }

                            data = mem.ToArray();
                        }
                    }
                    else if (isFirstSend)
                    {
                        // sending just session ID
                        isFirstSend = false;
                        data = (byte[])sessionID.Clone();
                    }
                }

                if (data != null)
                    socket.Send(endPoint, data);
            }
        }

        private void socket_Sent(object sender, SocketAsyncEventArgs e)
        {
            ThreadHelper.Sync(() =>
            {
                if (e.BytesTransferred > 0)
                {
                    // remove sent message
                    outbox.EndDequeue();

                    // start receiver loop (if needed)
                    if (isFirstReceive)
                    {
                        isFirstReceive = false;

                        StartReceive();
                    }

                    // if there is data to send - start another send
                    if (outbox.Count > 0)
                        StartSend();
                }
                else
                {
                    // connection was closed; restore last message
                    outbox.CancelDequeue();
                }

                e.Dispose();
            });
        }

        private void StartReceive()
        {
            if (State == TransportState.Connected)
                socket.Receive();
        }

        private void socket_Received(object sender, SocketAsyncEventArgs e)
        {
            if (e.BytesTransferred > 0)
            {
                byte[] res = new byte[e.BytesTransferred];
                Buffer.BlockCopy(e.Buffer, e.Offset, res, 0, e.BytesTransferred);

                if ((res != null) && (res.Length > 0))
                {
                    Pair<int, List<WaveMessage>> results = input.Process(res);

                    if ((results.Second != null) && (results.Second.Count > 0))
                    {
                        ThreadHelper.Sync(() =>
                        {
                            foreach (WaveMessage msg in results.Second)
                                OnNewMessage(msg);
                        });
                    }

                    if ((results.First > 0) && (results.First != endPoint.Port))
                    {
                        portOverride = results.First;

                        ThreadHelper.Sync(() => OnError(TransportErrorCode.ReconnectRequired));
                        return;
                    }
                }

                // loop forever
                StartReceive();
            }
            else if (e.BytesTransferred == 0)
            {
                // connection closed by server
                ThreadHelper.Sync(() => OnError(TransportErrorCode.LostConnection));
            }

            e.Dispose();
        }

        public override void Suspend()
        {
            if ((State != TransportState.Suspending) && (State != TransportState.Suspended))
            {
                State = TransportState.Suspending;

                socket.IsDeadParrot = true;

                socket.Connected -= socket_Connected;
                socket.Sent -= socket_Sent;
                socket.Received -= socket_Received;

                socket.Dispose();
                socket = null;

                isFirstSend = true;
                isFirstReceive = true;

                State = TransportState.Suspended;
            }
        }

        public override void Close()
        {
            // clean-up
            Suspend();

            isFirstSend = true;
            isFirstReceive = true;

            sessionID = null;

            // remove pending messages
            outbox.Clear();

            // clear received raw data
            if (input != null)
                input.Reset();

            // reset encryption keys
            serviceControl.ResetEncryption();

            // finally set the state and notify the world about it
            State = TransportState.Uninitialised;
        }

        public override void SendData(byte[] data)
        {
            outbox.Enqueue(data);

            StartSend();
        }

        public override void SetSessionID(byte[] sid)
        {
            if ((sid != null) && (sid.Length == 6))
            {
                sessionID = new byte[TCPSessionHeaderSize];

                Buffer.BlockCopy(sid, 0, sessionID, 2, 6);

                sessionID[0] = 6;
            }
        }
    }
}
