using System.Collections.Generic;
using System.IO;
using Wave.Common;
using Wave.Platform.Messaging;
using Wave.Services;

namespace Wave.Network
{
    public class HTTPInput : TransportInputBase
    {
        public HTTPInput()
            : base()
        {
        }

        /// <summary>
        /// Processes response of HTTP Gateway.
        /// </summary>
        /// <param name="buffer">Raw response data without HTTP headers.</param>
        /// <returns>HTTP Gateway session ID as byte array.</returns>
        public Pair<byte[], List<WaveMessage>> Process(byte[] buffer)
        {
            byte[] sessionID = new byte[HTTPTransport.HTTPSessionHeaderSize];
            List<WaveMessage> res = null;
            
            using (MemoryStream mem = new MemoryStream(buffer))
            {
                // session ID
                mem.Read(sessionID, 0, sessionID.Length);
                
                // reading eveything 
                while (1 == 1)
                {
                    int byte1 = mem.ReadByte();
                    int byte2 = mem.ReadByte();

                    if ((byte1 != -1) && (byte2 != -1))
                    {
                        int messageSize = byte1 | ((byte2 & 0x7F) << 8);
                        bool isTransactional = ((byte2 & 0x80) != 0x80);
                        
                        // read the raw data of the HTTP Gateway message
                        byte[] msg = new byte[messageSize];

                        mem.Read(msg, 0, msg.Length);

                        if ((Core.Network.TransactionalEncryption != null) && (Core.Network.StreamingEncryption != null))
                        {
                            if (isTransactional)
                                Core.Network.TransactionalEncryption.Decrypt(msg, msg.Length);
                            else
                                Core.Network.StreamingEncryption.Decrypt(msg, msg.Length);
                        }

                        List<WaveMessage> parsedMessages = ParseBucket(msg);

                        if (parsedMessages != null)
                        {
                            if (res != null)
                                res.AddRange(parsedMessages);
                            else
                                res = parsedMessages;
                        }
                    }
                    else
                        break;
                }
            }

            return new Pair<byte[], List<WaveMessage>>(sessionID, res);
        }
    }
}
