using System;
using System.Net;
using System.Net.Sockets;

namespace Wave.Network
{
    public sealed class TCPSocket : IDisposable
    {
        public bool IsDeadParrot { get; set; }

        public event EventHandler<SocketAsyncEventArgs> Connected;
        public event EventHandler<SocketAsyncEventArgs> Sent;
        public event EventHandler<SocketAsyncEventArgs> Received;

        private Socket socket = null;

        private bool disposed = false;

        public TCPSocket(AddressFamily addressFamily, SocketType socketType, ProtocolType protocolType)
        {
            IsDeadParrot = false;
            
            socket = new Socket(addressFamily, socketType, protocolType);
        }

        public void Dispose()
        {
            if (!disposed)
            {
                if (socket != null)
                    socket.Dispose();

                disposed = true;
            }
        }

        public void Connect(DnsEndPoint endPoint)
        {
            SocketAsyncEventArgs args = new SocketAsyncEventArgs();
            args.UserToken = socket;
            args.RemoteEndPoint = endPoint;
            args.Completed += new EventHandler<SocketAsyncEventArgs>(ConnectCompleted);

            if (!socket.ConnectAsync(args))
                ConnectCompleted(this, args);
        }

        public void Send(DnsEndPoint endPoint, byte[] data)
        {
            SocketAsyncEventArgs args = new SocketAsyncEventArgs();
            args.SetBuffer(data, 0, data.Length);
            args.RemoteEndPoint = endPoint;
            args.Completed += new EventHandler<SocketAsyncEventArgs>(SendCompleted);

            if (!socket.SendAsync(args))
                SendCompleted(this, args);
        }

        public void Receive()
        {
            SocketAsyncEventArgs args = new SocketAsyncEventArgs();
            byte[] response = new byte[4096];

            args.SetBuffer(response, 0, response.Length);
            args.Completed += new EventHandler<SocketAsyncEventArgs>(ReceiveCompleted);

            if (!socket.ReceiveAsync(args))
                ReceiveCompleted(this, args);
        }

        public void Close()
        {
            try
            {
                if (socket != null)
                {
                    socket.Close(2);
                    socket.Dispose();
                    socket = null;
                }
            }
            catch
            {
            }
        }

        private void ConnectCompleted(object sender, SocketAsyncEventArgs args)
        {
            if (!IsDeadParrot && Connected != null)
                Connected(this, args);
            else
                args.Dispose();
        }

        private void SendCompleted(object sender, SocketAsyncEventArgs args)
        {
            if (!IsDeadParrot && Sent != null)
                Sent(this, args);
            else
                args.Dispose();
        }

        private void ReceiveCompleted(object sender, SocketAsyncEventArgs args)
        {
            if (!IsDeadParrot && Received != null)
                Received(this, args);
            else
                args.Dispose();
        }
    }
}
