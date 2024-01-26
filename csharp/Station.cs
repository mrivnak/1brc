namespace OneBillionRows;

class Station {
    public float Min { get; set; } = float.MaxValue;
    public float Max { get; set; } = float.MinValue;
    public float Sum { get; set; } = 0.0f;
    public int Count { get; set; } = 0;

    public float Mean => Sum / Count;

    public void AddReading(float temperature) {
        Sum += temperature;
        Count++;
        if (temperature < Min) {
            Min = temperature;
        }
        if (temperature > Max) {
            Max = temperature;
        }
    }

    public override string ToString() {
        return $"{Min:F1}/{Mean:F1}/{Max:F1}";
    }
}
