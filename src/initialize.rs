use crate::data::{*};
use crate::network::{*};
use std::{fs, path::Path};
use rand::{*};

pub fn initializeConfig() -> Config {
    let config: Config = Config {
        cpuThreads: 32,
        gpuThreads: 128,
        attemptsPerPlayer: 262144,
        networkStructure: vec![24, 12],
        networkInputSize: 180,
        networkOutputSize: 4,
        gameOverReward: -20,
        piecePlaceReward: 1,
        lineClearReward: 80,
        makeHoleReward: 2,
        placedFlatReward: 12,
        seed: rand::random(),
        clockCyclesPerForcedFall: 3
    };
    return config
}

pub fn initializeNetworkCPU(
    lowerbound: &u16,
    upperbound: &u16
) -> NetworkCPU {
    let (biases, thresholds, packedBiases) = loadNetworks(lowerbound, upperbound);
    let networkCPU: NetworkCPU = NetworkCPU {
        config: initializeConfig(),
        lowerbound: *lowerbound,
        upperbound: *upperbound,
        biases: biases,
        thresholds: thresholds,
        tetrisGames: initializeTetrisGames(
            &(upperbound - lowerbound + 1)
        ),
        packedBiases: packedBiases
    };
    return networkCPU
}

pub fn initializeTetrisGames(
    numberOfGames: &u16
) -> Vec<Tetris> {
    let mut tetris = vec![];
    for _ in 0..*numberOfGames {
        tetris.push(Tetris {
            config: initializeConfig(),
            clock: 0,
            board: vec![vec![0; 10]; 20],
            sprite: vec![
                    vec![0, 0, 0, 0],
                    vec![0, 1, 0, 0],
                    vec![1, 1, 1, 0],
                    vec![0, 0, 0, 0]],
            currentPiece: 3,
            bag: vec![1, 2, 4, 5, 6, 7],
            rotation: 0,
            x: 4, //4
            y: 2,//-3
            losses: 0,
            reward: 0,
            score: 0.0,
            piecesPlaced: 0
            })
    }
    return tetris
}

pub fn makeFolders (
    folders: Vec<&str>
) {
    for folder in folders {
        let path = Path::new(folder);
        if !path.exists() {
            let _ = fs::create_dir(path);
        }
    }
}
