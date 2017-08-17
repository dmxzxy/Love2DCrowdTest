using System;
using Wave.Common;
using Wave.Platform.Messaging;
using Wave.Services;

namespace Wave.Network
{
    public abstract class TransportBase
    {
        /// <summary>
        /// The UDP/GPRS packet size for the transport layer.
        /// </summary>
        public const int MaximumSegmentSize = 396;

        public const int PriorityHeaderSize = 2;

        public TransportState State
        {
            get
            {
                return (TransportState)(int)state;
            }
            protected set
            {
                TransportState oldState = (TransportState)state.Exchange((int)value);

                if (oldState != value)
                    OnStateChange(value, oldState);
            }
        }

        public bool IsConnected
        {
            get { return State == TransportState.Connected; }
        }

        protected NetworkAgent.INetworkAgentControl serviceControl = null;

        private InterlockedInt state;

        public event DataEventHandler<object> DataReceived;
        public event EventHandler<TransportStateChangedEventArgs> StateChanged;
        public event DataEventHandler<TransportErrorCode> Error;

        #region Synchronisation objects

        protected object appInfoLock = new object();

        #endregion

        public TransportBase(NetworkAgent.INetworkAgentControl ctrl)
        {
            state = (int)TransportState.Uninitialised;

            serviceControl = ctrl;
        }

        public abstract void Open();
        public abstract void Connect();
        public abstract void Suspend();
        public abstract void Close();

        public abstract void SendData(byte[] data);

        public virtual void OnError(TransportErrorCode data)
        {
            if (Error != null)
                Error(this, new DataEventArgs<TransportErrorCode>(data));
        }

        public abstract void SetSessionID(byte[] sid);

        protected virtual void OnNewMessage(WaveMessage msg)
        {
            if (DataReceived != null)
                DataReceived(this, new DataEventArgs<object>(msg));
        }

        private void OnStateChange(TransportState newState, TransportState oldState)
        {
            if (StateChanged != null)
                StateChanged(this, new TransportStateChangedEventArgs(newState, oldState));
        }

        public static Enum ConvertWaveMessageID(WaveServerComponent appID, short msgID)
        {
            switch (appID)
            {
                case WaveServerComponent.UserManager:
                    return (UserManagerMessageID)msgID;

                case WaveServerComponent.CacheAgent:
                    return (CacheAgentMessageID)msgID;

                case WaveServerComponent.AggregatedMessageAgent:
                    return (AggregateMessageMessageID)msgID;

                case WaveServerComponent.NavigationAgent:
                    return (NaviAgentMessageID)msgID;

                case WaveServerComponent.DefinitionsAgent:
                    return (DefAgentMessageID)msgID;

                case WaveServerComponent.MediaAgent:
                    return (MediaAgentMessageID)msgID;
            }

            return WaveError.Empty;
        }
    }

    public class TransportStateChangedEventArgs : EventArgs
    {
        public TransportState New { get; private set; }
        public TransportState Old { get; private set; }

        public TransportStateChangedEventArgs(TransportState newState, TransportState oldState)
        {
            New = newState;
            Old = oldState;
        }
    }

    public enum TransportState
    {
        Uninitialised,
        Connecting,
        Connected,
        Disconnected,
        Suspending,
        Suspended
    }

    public enum TransportErrorCode
    {
        NoConnectionData,
        LostConnection,
        ReconnectRequired,
        DisconnectRequired
    }

    public static class TransportCode
    {
        public const string HTTP = "http";
        public const string TCP = "tcp";
        public const string UDP = "udp";
    }

    public enum WaveError
    {
        Empty = 0
    }
}
