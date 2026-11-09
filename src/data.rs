
#[derive(Debug)]
pub struct Config {
    pub cpuThreads: i32,
    pub gpuThreads: i32,
    pub attemptsPerPlayer: i64,
    pub networkStructure: Vec<u16>,
    pub networkInputSize: u16,
    pub networkOutputSize: u16,
    pub gameOverReward: i32,
    pub piecePlaceReward: i32,
    pub lineClearReward: i32,
    pub makeHoleReward: i32,
    pub placedFlatReward: i32,
    pub seed: i32,
    pub clockCyclesPerForcedFall: i32
}

#[derive(Debug)]
pub struct Tetris {
    pub config: Config,
    pub clock: i16,
    pub board: Vec<Vec<u16>>,
    pub sprite: Vec<Vec<u16>>,
    pub currentPiece: u16,
    pub bag: Vec<u16>,
    pub rotation: u16,
    pub x: i32,
    pub y: i32,
    pub losses: u32,
    pub reward: i32,
    pub score: f64,
    pub piecesPlaced: u32
}

#[derive(Debug)]
pub struct NetworkCPU {
    pub config: Config,
    pub lowerbound: u16,
    pub upperbound: u16,
    pub biases: Vec<Vec<Vec<bool>>>,
    pub thresholds: Vec<Vec<Vec<u16>>>,
    pub tetrisGames: Vec<Tetris>,
    pub packedBiases: Vec<Vec<Vec<Vec<u64>>>>,
}

#[derive(Debug)]
pub enum Direction {
    ROTATE,
    DOWN,
    LEFT,
    RIGHT
}

pub enum Reward {
    Place,
    LineClear,
    GameOver,
    MakeHole,
    PlacePiece
}
