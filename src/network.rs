use std::{path::Path};
use crate::data::{*};
use crate::tetris::{*};
use savefile::{save_file, load_file};
use rand::{*};
use crate::initialize::{*};

pub fn stepTetris(
    tetris: &mut Tetris,
    packedBiases: &Vec<Vec<Vec<u64>>>,
    thresholds: &Vec<Vec<u16>>
){
    moveTetris(computeNetwork(
        packedBiases,
        thresholds,
        &tetris.config.networkOutputSize,
        &tetris.config.networkInputSize,
        &tetris.sprite,
        &tetris.currentPiece,
        &tetris.rotation,
        &tetris.x,
        &tetris.y,
        &tetris.board
    ), tetris);
}

pub fn loadNetworks(
    lowerbound: &u16,
    upperbound: &u16
) -> (Vec<Vec<Vec<bool>>>, Vec<Vec<Vec<u16>>>, Vec<Vec<Vec<Vec<u64>>>>) {
    let mut biases: Vec<Vec<Vec<bool>>> = vec![];
    let mut thresholds: Vec<Vec<Vec<u16>>> = vec![];
    let mut packedBiases: Vec<Vec<Vec<Vec<u64>>>> = vec![];
    for i in *lowerbound..=*upperbound {
        let biasPath: String = format!("networks/bias_{}.bin", lowerbound + i);
        let thresholdPath: String = format!("networks/threshold_{}.bin", lowerbound + i);
        let loadedBiases: Vec<Vec<bool>> = loadBiases(&biasPath);
        let loadedThresholds: Vec<Vec<u16>> = loadThresholds(&thresholdPath);
        let loadedPackedBiases: Vec<Vec<Vec<u64>>> = packBiases(&loadedBiases);
        biases.push(loadedBiases);
        thresholds.push(loadedThresholds);
        packedBiases.push(loadedPackedBiases);
    }
    return (biases, thresholds, packedBiases);

}

fn loadBiases(
    path: &String
) -> Vec<Vec<bool>> {
    let path = Path::new(path);
    if path.exists() {
        return load_file(path, 0).unwrap();
    }
    else {
        let biases = generateBiases();
        save_file(path, 0, &biases).unwrap();
        return biases;
    }
}

fn loadThresholds(
    path: &String
) -> Vec<Vec<u16>> {
    let path = Path::new(path);
    if path.exists() {
        return load_file(path, 0).unwrap();
    }
    else {
        let thresholds: Vec<Vec<u16>> = generateThresholds();
        save_file(path, 0, &thresholds).unwrap();
        return thresholds;
    }
}

pub fn generateBiases() -> Vec<Vec<bool>>
{
    let config: Config = initializeConfig();
    let mut biases: Vec<Vec<bool>> = vec![];
    let mut layers: Vec<u16> = vec![config.networkInputSize];
    for i in 0..config.networkStructure.len() {
        layers.push(config.networkStructure[i]);
    }
    layers.push(config.networkOutputSize);
    for i in 0..layers.len() - 1 {
        biases.push(vec![false; (layers[i] * layers[i + 1]) as usize]);
        for k in 0..biases[i].len() {
            biases[i][k] = rand::random::<bool>();
        }
    }
    return biases
}

pub fn generateThresholds() -> Vec<Vec<u16>>
{
    let config: Config = initializeConfig();
    let mut thresholds: Vec<Vec<u16>> = vec![];
    for i in 0..config.networkStructure.len() {
        thresholds.push(vec![0; config.networkStructure[i] as usize])
    }
    for i in 0..thresholds[0].len() {
        thresholds[0][i] = rand::rng().random_range(2..(config.networkInputSize as f32 / 1.25) as u16);
    }
    for i in 0..thresholds[1].len() {
        thresholds[1][i] = rand::rng().random_range(2..(thresholds[0].len() as f32 / 1.25) as u16);
    }
    return thresholds
}

pub fn packBiases(
    biases: &Vec<Vec<bool>>
) -> Vec<Vec<Vec<u64>>> {
    let mut packedLayers: Vec<Vec<Vec<u64>>> = vec![];
    let mut previousBits = 180;
    for layer in 0..biases.len() {
        let neuronCount = biases[layer].len() / previousBits;
        assert_eq!(
            biases[layer].len() % previousBits,
                   0,
                   "Bias layer has an invalid number of weights!"
        );
        let groups = (neuronCount + 3) / 4;
        let chunks = (previousBits + 15) / 16;
        let mut packed: Vec<Vec<u64>> =
        vec![vec![0; chunks]; groups];
        for neuron in 0..neuronCount {
            let group = neuron / 4;
            let lane = neuron % 4;
            for inputIndex in 0..previousBits {
                if biases[layer][neuron * previousBits + inputIndex] {
                    let chunk = inputIndex / 16;
                    let bit = lane * 16 + inputIndex % 16;
                    packed[group][chunk] |= 1u64 << bit;
                }
            }
        }
        packedLayers.push(packed);
        previousBits = neuronCount;
    }
    packedLayers
}

fn layerCount(layer: usize) -> usize {
    let config = initializeConfig();
    if layer < config.networkStructure.len() {
        return config.networkStructure[layer] as usize;
    }
    return config.networkOutputSize as usize;
}


pub fn popCount4x16(mut x: u64) -> u64 {
    x =  x - ((x >> 1) & 0x5555555555555555);
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0F;
    x = (x + (x >> 8)) & 0x00FF00FF00FF00FF;
    x
}

fn runPackedLayer(
    input_chunks: &[u64],
    packed_weights: &[Vec<u64>],
    thresholds: &[u16],
    network_input_size: usize,
    neuron_count: usize,
    use_threshold: bool,
) -> Vec<u16> {
    let groups = (neuron_count + 3) / 4;
    let chunk_count = input_chunks.len();
    let mut outputs = vec![0u16; neuron_count];

    for group in 0..groups {
        let mut accumulated: u64 = 0;

        for chunk in 0..chunk_count {
            let remaining = network_input_size - chunk * 16;
            let valid_bits = remaining.min(16);
            let base_mask = (1u64 << valid_bits) - 1;
            let lane_mask =
            base_mask
            | (base_mask << 16)
            | (base_mask << 32)
            | (base_mask << 48);
            let input_word =
            input_chunks[chunk] * 0x0001_0001_0001_0001u64;
            let mut matches =
            !(packed_weights[group][chunk] ^ input_word);
            matches &= lane_mask;
            accumulated += popCount4x16(matches);
        }
        for lane in 0..4 {
            let neuron = group * 4 + lane;
            if neuron < neuron_count {
                let count =
                ((accumulated >> (lane * 16)) & 0xFFFF) as u16;

                if use_threshold {
                    outputs[neuron] =
                    if count >= thresholds[neuron] {
                        1
                    } else {
                        0
                    };
                } else {
                    outputs[neuron] = count;
                }
            }
        }
    }
    return outputs
}

fn packActivations(activations: &[u16]) -> Vec<u64> {
    let mut chunks = vec![0u64; (activations.len() + 15) / 16];
    for i in 0..activations.len() {
        if activations[i] != 0 {
            chunks[i / 16] |= 1u64 << (i % 16);
        }
    }
    return chunks
}

fn computeNetwork (
    biases: &Vec<Vec<Vec<u64>>>,
    thresholds: &Vec<Vec<u16>>,
    networkOutputSize: &u16,
    networkInputSize: &u16,
    sprite: &Vec<Vec<u16>>,
    currentPiece: &u16,
    rotation: &u16,
    x: &i32,
    y: &i32,
    board: &Vec<Vec<u16>>
) -> Direction {
    let mut firstLayer: Vec<bool> = vec![false; *networkInputSize as usize];
    for sy in 0..4 {
        for sx in 0..4 {
            if sprite[sy][sx] != 0 {
                firstLayer[sy * 4 +sx] = true
            }
        }
    }
    firstLayer[(15 + currentPiece) as usize] = true;
    firstLayer[(23 + rotation) as usize] = true;
    firstLayer[(29+x) as usize] = true;
    firstLayer[(41+y) as usize] = true;
    let mut xVal = x - 8;
    let mut value: i32;
    for i in 0..20 {
        let mut counter = 0;
        if 0 <= xVal && xVal <= 9 {
            while counter + 1 + y < 20 && ((y + counter + 1 <0) || (board[(y + counter + 1) as usize][xVal as usize] == 0)) {
                counter += 1;
            }
            value = counter;
        } else {
            value = 26;
        }
        for bit in 0..5 {
            firstLayer[60+i*5+bit] = ((value >> bit) & 1) != 0
        }
    xVal += 1;
    }
    let mut yOffset: Vec<usize> = vec![0; 4];
    let mut foundBit: Vec<bool> = vec![false; 4];
    for sx in 0..4 {
        for sy in 0..4 {
            if sprite[sy][sx] != 0 {
                yOffset[sx] = sy;
                foundBit[sx] = true
            }
        }
    }
    for i in 0..4 {
        let mut value = 31;
        if foundBit[i] {
            xVal = x + i as i32;
            let yVal = y + yOffset[i] as i32;
            if 0 <= xVal && xVal <= 9 {
                let mut counter = 0;
                while
                    counter + 1 + yVal < 20 && (
                       (yVal + counter + 1 < 0) || (board[(yVal + counter + 1) as usize][xVal as usize] == 0)
                    )
                {
                    counter += 1
                }
                value = counter
            } else {
                value = 26
            }
        }
        for bit in 0..5 {
            firstLayer[60 + (20 + i) * 5 + bit] = ((value >> bit) & 1) != 0
        }
    }
    let mut inputChunks = vec![0u64; (*networkInputSize as usize + 15) / 16];
    for i in 0..*networkInputSize as usize {
        if firstLayer[i] {
            inputChunks[i / 16] |= 1u64 << (i % 16);
        }
    }
    let firstActivations = runPackedLayer(
        &inputChunks,
        &biases[0],
        &thresholds[0],
        *networkInputSize as usize,
        24,
        true
    );
    let secondInput = packActivations(&firstActivations);
    let secondActivations = runPackedLayer(
        &secondInput,
        &biases[1],
        &thresholds[1],
        24,
        12,
        true
    );
    let thirdInput = packActivations(&secondActivations);
    let output = runPackedLayer(
        &thirdInput,
        &biases[2],
        &[],
        12,
        *networkOutputSize as usize,
        false
    );
    let bestIndex = output
    .iter()
    .enumerate()
    .max_by_key(|&(_, score)| score)
    .unwrap()
    .0;

    let direction = match bestIndex {
        0 => Direction::ROTATE,
        1 => Direction::DOWN,
        2 => Direction::LEFT,
        3 => Direction::RIGHT,
        _ => unreachable!(),
    };
    return direction
}
