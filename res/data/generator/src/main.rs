use std::{fs::{self, File}, io::{BufRead, BufReader, BufWriter, Write}, path::Path};

use rand::seq::SliceRandom;

struct Station {
    name: String,
    avg_temp: f32,
}

fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    if args.len() != 3 {
        println!("Usage: {} <path> <size>", args[0]);
        return;
    }

    let path = Path::new(&args[1]);
    let size = args[2].parse::<usize>().expect("invalid size");

    let start = std::time::Instant::now();

    let stations_data_path = Path::new("../weather_stations.csv");
    let stations_file = File::open(stations_data_path).expect("failed to read stations data");
    let reader = BufReader::new(stations_file);

    let mut stations = Vec::new();
    for line in reader.lines() {
        let line = line.expect("failed to read line");
        let Some(parts) = line.split_once(';') else {
            // First two lines are comments
            continue;
        };

        let name = parts.0.to_string();
        let avg_temp = parts.1.parse::<f32>().expect("invalid temperature");
        stations.push(Station { name, avg_temp });
    }

    let out_file = File::create(path).expect("failed to open output file");
    let mut writer = BufWriter::new(out_file);
    let mut rng = rand::thread_rng();

    for _ in 0..size {
        let station = stations.choose(&mut rng).unwrap();
        writer.write_all(format!("{};{}\n", station.name, station.avg_temp).as_bytes()).expect("failed to write line");
    }
    writer.flush().expect("failed to flush output file");

    let file_size = match fs::metadata(path).expect("failed to read file metadata").len() {
        size if size < 1024 => format!("{}B", size),
        size if size < 1024 * 1024 => format!("{:.2}KiB", size as f32 / 1024.0),
        size if size < 1024 * 1024 * 1024 => format!("{:.2}MiB", size as f32 / 1024.0 / 1024.0),
        size => format!("{:.2}GiB", size as f32 / 1024.0 / 1024.0 / 1024.0),
    };

    println!("Generated {} lines ({}) in {:.3}s", size, file_size, start.elapsed().as_secs_f32());
}
