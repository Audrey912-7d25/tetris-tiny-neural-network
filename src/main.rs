#![allow(non_snake_case)]
#![allow(unused_variables)]
#![allow(unused_imports)]
mod data;
use crate::data::{*};
mod initialize;
use crate::initialize::{*};
mod tetris;
use crate::tetris::{*};
mod network;
use crate::network::{*};
mod display;
use crate::display::{*};
use std::time::Instant;


fn main() {
    let lowerbound: u16 = 0;
    let upperbound: u16 = 0;
    let config: Config = initializeConfig();
    makeFolders(vec!["networks", "best"]);
    let mut networkCPU: NetworkCPU = initializeNetworkCPU(
        &lowerbound,
        &upperbound
    );


    displayTetrisState(&networkCPU.tetrisGames[0]);
    let start = Instant::now();
    while networkCPU.tetrisGames[0].losses as i64 <= config.attemptsPerPlayer {
        stepTetris(
            &mut networkCPU.tetrisGames[0],
            &networkCPU.packedBiases[0],
            &networkCPU.thresholds[0]
        );
    }
    println!("{} games per second for {} steps. {} time passed", config.attemptsPerPlayer as f32 / (start.elapsed().as_millis() as f32 / 1000.0) as f32, config.attemptsPerPlayer, start.elapsed().as_millis());
    displayTetrisState(&networkCPU.tetrisGames[0]);
}
