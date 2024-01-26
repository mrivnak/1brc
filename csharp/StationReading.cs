namespace OneBillionRows;

class StationReading {
    public string StationName { get; set; }
    public float Temperature { get; set; }

    public StationReading(string stationName, float temperature) {
        StationName = stationName;
        Temperature = temperature;
    }

    public static StationReading FromCsv(string csvLine) {
        var values = csvLine.Split(';');
        var stationName = values[0];
        var temperature = float.Parse(values[1]);
        return new StationReading(stationName, temperature);
    }
}