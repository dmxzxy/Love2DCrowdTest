using System.Collections.Generic;
using System.IO;
using Wave.Platform.Messaging;

namespace Wave.Network
{
    public abstract class TransportInputBase
    {
        // message assemblers
        protected WaveMessageAssembler streamingMessagesBucket = new WaveMessageAssembler();     // priority 0 (out of 6)
        protected WaveMessageAssembler transactionalMessagesBucket = new WaveMessageAssembler(); // priority 3 (out of 6)

        public TransportInputBase()
        {
        }

        /// <summary>
        /// Parses raw messages and sorts individual packets.
        /// </summary>
        /// <param name="bucket">Raw message data.</param>
        protected List<WaveMessage> ParseBucket(byte[] bucket)
        {
            if (bucket.Length == 0)
                return null;

            List<WaveMessage> res = null;

            using (MemoryStream mem = new MemoryStream(bucket))
            {
                while (mem.Position < (mem.Length - 1))
                {
                    // last 4 bits of first byte are the priority
                    // the 8 bits of the second byte are the first 8 bits of the 12 bit packet size
                    // while the first 4 bits of the first byte are the last 4 bits of the 12 bit packet size
                    int byte1 = mem.ReadByte();

                    if (byte1 != -1)
                    {
                        int priority = byte1 & 0x0F;
                        int packetSize = mem.ReadByte() << 4;
                        packetSize |= (byte1 >> 4);

                        WaveMessageAssembler asm = GetAssembler(priority);

                        if (asm != null)
                        {
                            byte[] packet = new byte[packetSize];
                            mem.Read(packet, 0, packet.Length);

                            asm.Add(packet);

                            if (asm.IsComplete)
                                res = asm.ToWaveMessages();
                        }
                    }
                }
            }

            return res;
        }

        public virtual void Reset()
        {
            if (streamingMessagesBucket != null)
                streamingMessagesBucket.Reset();

            if (transactionalMessagesBucket != null)
                transactionalMessagesBucket.Reset();
        }

        protected WaveMessageAssembler GetAssembler(int priority)
        {
            switch (priority)
            {
                case 0:
                    return streamingMessagesBucket;

                case 3:
                    return transactionalMessagesBucket;
            }

            return null;
        }
    }
}
