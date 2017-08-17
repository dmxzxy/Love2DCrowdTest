using System;
using System.Collections.Generic;
using System.IO;
using Wave.Common;
using Wave.Platform.Messaging;
using Wave.Services;

namespace Wave.Network
{
    public class TCPInput : TransportInputBase
    {
        private bool isFirst = true;

        public TCPInput()
            : base()
        {
        }

        /// <summary>
        /// Processes TCP responses.
        /// </summary>
        /// <param name="buffer">Raw response data without TCP header.</param>
        /// <returns>Port number (if available).</returns>
        public Pair<int, List<WaveMessage>> Process(byte[] buffer)
        {
            int port = -1;
            List<WaveMessage> res = null;
            
            using (MemoryStream mem = new MemoryStream(buffer))
            {
                if (isFirst)
                {
                    isFirst = false;

                    mem.ReadByte();
                    mem.ReadByte();

                    port = mem.ReadShort();
                }

                if (port != 0)
                {
                    // reading eveything 
                    while (1 == 1)
                    {
                        int messageSize = unfinishedRemainder;
                        bool isTransactional = unfinishedTransactional;
                        
                        if (tempStore == null)
                        {
                            int byte1 = mem.ReadByte();
                            int byte2 = mem.ReadByte();

                            if ((byte1 == -1) || (byte2 == -1))
                                break;

                            messageSize = byte1 | ((byte2 & 0x7F) << 8);
                            isTransactional = ((byte2 & 0x80) != 0x80);
                        }

                        // try reading the raw data of the message
                        byte[] msg = new byte[messageSize];

                        int readResult = mem.Read(msg, 0, msg.Length);

                        if (readResult == messageSize)
                        {
                            // everything is fine
                            byte[] chunk = null;

                            if (tempStore != null)
                            {
                                chunk = ByteArrayHelper.Combine(tempStore, msg);
                                tempStore = null;
                            }
                            else
                                chunk = msg;
                            
                            if (chunk != null)
                            {
                                // decrypt if needed
                                if ((Core.Network.TransactionalEncryption != null) && (Core.Network.StreamingEncryption != null))
                                {
                                    if (isTransactional)
                                        Core.Network.TransactionalEncryption.Decrypt(chunk, chunk.Length);
                                    else
                                        Core.Network.StreamingEncryption.Decrypt(chunk, chunk.Length);
                                }

                                // parse away
                                List<WaveMessage> parsedMessages = ParseBucket(chunk);

                                if (parsedMessages != null)
                                {
                                    if (res != null)
                                        res.AddRange(parsedMessages);
                                    else
                                        res = parsedMessages;
                                }
                            }

                            // reset temporary variabless
                            unfinishedRemainder = 0;
                            unfinishedTransactional = false;
                            tempStore = null;
                        }
                        else
                        {
                            // not enough data received
                            int remainder = messageSize - readResult;

                            if (remainder > 0)
                            {
                                byte[] chunk = new byte[readResult];
                                Buffer.BlockCopy(msg, 0, chunk, 0, readResult);

                                if (tempStore != null)
                                    tempStore = ByteArrayHelper.Combine(tempStore, chunk);
                                else
                                    tempStore = chunk;

                                // set temporary variabless
                                unfinishedRemainder = remainder;
                                unfinishedTransactional = isTransactional;
                            }

                            DebugHelper.Trace("Incomplete TCP packet: {0} bytes remaining.", unfinishedRemainder);
                            break;
                        }
                    }
                }
            }

            return new Pair<int, List<WaveMessage>>(port, res);
        }

        private int unfinishedRemainder = 0;
        private bool unfinishedTransactional = false;
        private byte[] tempStore = null;

        public override void Reset()
        {
            base.Reset();

            isFirst = true;

            unfinishedRemainder = 0;
            unfinishedTransactional = false;
            tempStore = null;
        }
    }
}
