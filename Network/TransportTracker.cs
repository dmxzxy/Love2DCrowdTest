using System;
using Wave.Common;
using Wave.Services;

namespace Wave.Network
{
    public class TransportTracker
    {
        public bool IsStalled
        {
            get { return (lastTransport == String.Empty); }
        }
        
        private InterlockedInt retries = 3;
        private string lastTransport = null;

        private NetworkAgent.INetworkAgentControl serviceControl = null;
        
        public TransportTracker(NetworkAgent.INetworkAgentControl ctrl)
        {
            serviceControl = ctrl;
        }

        public TransportTrackerResult GetNext()
        {
            TransportTrackerAction action = TransportTrackerAction.ItIsAllOver;
            TransportBase transport = null;

            if (!String.IsNullOrEmpty(lastTransport) && (retries > 0))
            {
                action = TransportTrackerAction.RetryExistingTransport;

                retries--;
            }
            else if (IsStalled)
            {
                action = TransportTrackerAction.ItIsAllOver;
            }
            else
            {
                transport = FindNextTransport();

                if (transport == null)
                    action = TransportTrackerAction.ItIsAllOver;
                else
                    action = TransportTrackerAction.LoadNewTransport;
            }

            return new TransportTrackerResult(action, transport);
        }

        public void Reset()
        {
            retries = 3;
            lastTransport = null;
        }

        private TransportBase FindNextTransport()
        {
            TransportBase res = null;

            if (lastTransport == null)
            {
                // first call -> return TCP
                res = new TCPTransport(serviceControl);
                retries = 3;
                lastTransport = TransportCode.TCP;
            }
            else if (lastTransport == TransportCode.TCP)
            {
                // call after TCP -> return HTTP
                res = new HTTPTransport(serviceControl);
                retries = 3;
                lastTransport = TransportCode.HTTP;
            }
            else if (lastTransport == TransportCode.HTTP)
            {
                // call after HTTP -> return nothing
                res = null;
                retries = 0;
                lastTransport = String.Empty;
            }
            else if (lastTransport == String.Empty)
            {
                // call when stalled -> return nothing
                res = null;
                retries = 0;
                lastTransport = String.Empty;
            }

            return res;
        }
    }

    public struct TransportTrackerResult
    {
        public TransportTrackerAction Action { get; private set; }
        public TransportBase Transport { get; private set; }

        public TransportTrackerResult(TransportTrackerAction action, TransportBase transport = null)
            : this()
        {
            Action = action;
            Transport = transport;
        }
    }

    public enum TransportTrackerAction
    {
        RetryExistingTransport,
        LoadNewTransport,
        ItIsAllOver
    }
}
