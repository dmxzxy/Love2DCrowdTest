﻿namespace Evaders.Core.Utility
{
    using System;
    using System.Collections.Concurrent;
    using System.Collections.Generic;
    using System.Linq;
    using Newtonsoft.Json;
    using Newtonsoft.Json.Serialization;

    public class GameContractResolver : DefaultContractResolver
    {
        private readonly ConcurrentDictionary<Type, IList<JsonProperty>> _cache = new ConcurrentDictionary<Type, IList<JsonProperty>>();

        protected override IList<JsonProperty> CreateProperties(Type type, MemberSerialization memberSerialization)
        {
            if (!_cache.ContainsKey(type))
                _cache.TryAdd(type, base.CreateProperties(type, memberSerialization).Where(item => item.AttributeProvider.GetAttributes(typeof (JsonPropertyAttribute), true).Any()).ToList());

            return _cache[type];
        }

        //{

        //protected override IList<JsonProperty> CreateProperties(Type type, MemberSerialization memberSerialization)
        //    return new JsonProperty[0]; //base.CreateProperties(type, memberSerialization).Where(item => item.Writable).ToList();
        //}
    }
}