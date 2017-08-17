using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Windows.Threading;
using Wave.Common;
using Wave.Platform.Messaging;
using Wave.Services;

namespace Wave.Network
{
    public class HTTPTransport : TransportBase
    {
        public const int HTTPSessionHeaderSize = 4;
        public const int RDPHeaderSize = 2;
        
        private AsyncQueue<byte[]> outbox = new AsyncQueue<byte[]>();
        private HTTPInput input = null;

        private DispatcherTimer keepAliveTimer = null;
        private DispatcherTimer timeOutTimer = null;

        private byte[] sessionID = new byte[HTTPSessionHeaderSize];
        private bool isFirst = true;

        private HTTPRequestData currentState = null;
        
        public HTTPTransport(NetworkAgent.INetworkAgentControl ctrl)
            : base(ctrl)
        {
        }
        
        public override void Open()
        {
            if (State == TransportState.Uninitialised)
            {
                if (!Core.Application.HasHTTP)
                {
                    OnError(TransportErrorCode.NoConnectionData);
                    return;
                }

                input = new HTTPInput();
                sessionID = new byte[HTTPSessionHeaderSize];

                keepAliveTimer = new DispatcherTimer();
                keepAliveTimer.Interval = TimeSpan.FromSeconds(5);
                keepAliveTimer.Tick += new EventHandler(keepAliveTimer_Tick);

                timeOutTimer = new DispatcherTimer();
                timeOutTimer.Interval = TimeSpan.FromSeconds(20);
                timeOutTimer.Tick += new EventHandler(timeOutTimer_Tick);
                
                Connect();
            }
        }

        public override void Connect()
        {
            if (State != TransportState.Connected)
            {
                State = TransportState.Connecting;

                keepAliveTimer.Start();

                StartSend();
            }
        }

        private void StartSend()
        {
            if ((State == TransportState.Connected) || (State == TransportState.Connecting))
            {
                if (outbox.CanDequeue)
                {
                    string appUri = String.Format("http://{0}:{1}/HTTPGateway/requestor", Core.Application.HTTP.Host, Core.Application.HTTP.Port);

                    if (appUri != null)
                    {
                        byte[] toSend = null;
                        byte[] temp = outbox.BeginDequeue();

                        if (temp != null)
                        {
                            using (MemoryStream mem = new MemoryStream())
                            {
                                // session ID
                                mem.WriteBytes(sessionID);

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

                                toSend = mem.ToArray();
                            }
                        }
                        else
                        {
                            // sending just session ID
                            toSend = (byte[])sessionID.Clone();

                            if (isFirst)
                                isFirst = false;
                        }

                        if (toSend != null)
                        {
                            HttpWebRequest connection = WebRequest.CreateHttp(appUri);
                            connection.Method = "POST";

                            // create state object
                            HTTPRequestData state = new HTTPRequestData() { Connection = connection, Data = toSend };

                            // save state for possible cancellation
                            currentState = state;

                            // start timeout timer
                            timeOutTimer.Start();

                            // do request
                            connection.BeginGetRequestStream(RequestCallback, state);
                        }
                    }
                }
            }
        }

        private void RequestCallback(IAsyncResult asyncResult)
        {
            HTTPRequestData state = asyncResult.AsyncState as HTTPRequestData;

            if (state != null)
            {
                Stream requestStream = null;

                try
                {
                    requestStream = state.Connection.EndGetRequestStream(asyncResult);
                }
                catch
                {
                    requestStream = null;

                    OnError(TransportErrorCode.LostConnection);
                }

                if (requestStream != null)
                {
                    requestStream.Write(state.Data, 0, state.Data.Length);
                    requestStream.Close();

                    state.Connection.BeginGetResponse(ResponseCallback, state);
                }
            }
        }

        private void ResponseCallback(IAsyncResult asyncResult)
        {
            HTTPRequestData state = asyncResult.AsyncState as HTTPRequestData;

            if (state != null)
            {
                HttpWebResponse response = null;

                try
                {
                    response = state.Connection.EndGetResponse(asyncResult) as HttpWebResponse;
                }
                catch
                {
                    response = null;
                    
                    OnError(TransportErrorCode.LostConnection);
                }

                if (response != null)
                {
                    byte[] res = null;

                    if (response.StatusCode == HttpStatusCode.OK)
                    {
                        using (Stream st = response.GetResponseStream())
                            res = st.ReadAll();
                    }

                    if (IsValidResponse(res))
                    {
                        // remove sent message
                        outbox.EndDequeue();

                        // set state
                        State = TransportState.Connected;

                        // process response
                        Pair<byte[], List<WaveMessage>> results = input.Process(res);

                        if ((results.First != null) && (results.First.Length == HTTPSessionHeaderSize))
                            sessionID = (byte[])results.First.Clone();

                        if ((results.Second != null) && (results.Second.Count > 0))
                        {
                            ThreadHelper.Sync(
                                () =>
                                {
                                    foreach (WaveMessage msg in results.Second)
                                        OnNewMessage(msg);
                                });
                        }
                    }
                    else
                    {
                        // restore last message
                        outbox.CancelDequeue();

                        if (response.StatusCode != HttpStatusCode.OK)
                            OnError(TransportErrorCode.LostConnection);
                    }

                    ThreadHelper.Sync(
                        () =>
                        {
                            OnRequestEnded();

                            // if there is data to send - start another send
                            if (outbox.Count > 0)
                                StartSend();
                        });

                    State = TransportState.Connecting;
                }
            }
        }

        public override void Suspend()
        {
            State = TransportState.Suspending;

            if (currentState != null)
                currentState.Connection.Abort();

            State = TransportState.Suspended;
        }

        public override void Close()
        {
            // clean-up
            Suspend();

            isFirst = true;
            sessionID = new byte[HTTPSessionHeaderSize];

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

        public override void OnError(TransportErrorCode data)
        {
            ThreadHelper.Sync(
                () =>
                {
                    base.OnError(data);
                });
        }

        public override void SendData(byte[] data)
        {
            outbox.Enqueue(data);

            StartSend();
        }

        public override void SetSessionID(byte[] sid)
        {
            // this is useless for HTTP transport
        }

        private void keepAliveTimer_Tick(object sender, EventArgs e)
        {
            if (currentState == null)
                StartSend();
        }

        private void timeOutTimer_Tick(object sender, EventArgs e)
        {
            if (currentState != null)
                currentState.Connection.Abort();
        }

        private void OnRequestEnded()
        {
            currentState = null;

            timeOutTimer.Stop();
        }

        private bool IsValidResponse(byte[] data)
        {
            // no response
            if ((data == null) || (data.Length < HTTPSessionHeaderSize))
                return false;

            // null response
            if ((data.Length == HTTPSessionHeaderSize) &&
                (data[0] == 0) && (data[1] == 0) && (data[2] == 0) && (data[3] == 0))
                return false;

            // some useful data is in there!
            return true;
        }

        private class HTTPRequestData
        {
            public HttpWebRequest Connection { get; set; }
            public byte[] Data { get; set; }
        }
    }
}
