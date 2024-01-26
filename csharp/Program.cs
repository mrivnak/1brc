using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;

namespace OneBillionRows;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length != 1)
        {
            Console.WriteLine("Usage: OneBillionRows <FILE>");
            return;
        }

        // Calculate min mean and max
        var lines = File.ReadLines(args[0]);
        var stations = new Dictionary<string, Station>();

        foreach (var line in lines)
        {
            var reading = StationReading.FromCsv(line);
            if (stations.ContainsKey(reading.StationName))
            {
                var station = stations[reading.StationName];
                station.AddReading(reading.Temperature);
            }
            else
            {
                var station = new Station();
                station.AddReading(reading.Temperature);
                stations.Add(reading.StationName, station);
            }
        }

        var writerOptions = new JsonWriterOptions
        {
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        };

        using var stream = new MemoryStream();
        using var writer = new Utf8JsonWriter(stream, writerOptions);
        writer.WriteStartObject();
        foreach (var station in stations)
        {
            writer.WritePropertyName(station.Key);
            writer.WriteStringValue(station.Value.ToString());
        }
        writer.WriteEndObject();
        writer.Flush();

        var json = Encoding.UTF8.GetString(stream.ToArray());
        Console.WriteLine(json);
    }
}
