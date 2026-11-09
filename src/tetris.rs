use rand::{SeedableRng, Rng};
use rand::rngs::StdRng;
use crate::data::{*};

pub fn moveTetris(
    direction: Direction,
    tetris: &mut Tetris
) {
    match direction {
        Direction::LEFT => {
            let mut allowMoveLeft: bool = true;
            for y in 0..tetris.sprite.len() {
                for x in 0..tetris.sprite[0].len() {
                    if tetris.sprite[y][x] != 0  && (y as i32 +tetris.y >= 0){
                        if (0 > tetris.x+x as i32 -1) | (9 < tetris.x+x as i32 -1){
                            allowMoveLeft = false
                        } else if tetris.board[(y as i32 +tetris.y) as usize][(x as i32 +tetris.x - 1) as usize] != 0 &&
                            y as i32+tetris.y >= 20 {
                                allowMoveLeft = false
                            }
                    }
                    if tetris.sprite[y][x] != 0 && (0 > tetris.x+x as i32 -1) | (9 < tetris.x+x as i32 -1) {
                        allowMoveLeft = false
                    }
                }
            }
            if allowMoveLeft {
                tetris.x -= 1
            }
        }
        Direction::RIGHT => {
            let mut allowMoveRight: bool = true;
            for y in 0..tetris.sprite.len() {
                for x in 0..tetris.sprite[0].len() {
                    if tetris.sprite[y][x] != 0  && (y as i32 +tetris.y >= 0){
                        if (0 > tetris.x+x as i32 +1) | (9 < tetris.x+x as i32 +1){
                            allowMoveRight = false
                        } else if tetris.board[(y as i32 +tetris.y) as usize][(x as i32 +tetris.x + 1) as usize] != 0 &&
                            y as i32+tetris.y >= 20 {
                            allowMoveRight = false
                            }
                    }
                    if tetris.sprite[y][x] != 0 && (0 > tetris.x+x as i32 +1) | (9 < tetris.x+x as i32 +1) {
                        allowMoveRight = false
                    }
                }
            }
            if allowMoveRight {
                tetris.x += 1
            }
        }
        Direction::ROTATE => {
            let mut allowMoveRotate: bool = true;
            let testSprite: Vec<Vec<u16>> = rotateSprite(&tetris.sprite);
            for y in 0..testSprite.len() {
                for x in 0..testSprite[0].len() {
                    if testSprite[y][x] != 0 {
                        if (0 > tetris.x+x as i32) | (9 < tetris.x+x as i32) | (19 < tetris.y+y as i32) {
                            allowMoveRotate = false
                        } else if tetris.y + y as i32 > 0 {
                            if tetris.board[(y as i32 +tetris.y) as usize][(x as i32 +tetris.x) as usize] != 0 {
                                allowMoveRotate = false
                            }
                        }
                    }
                }
            }
            if allowMoveRotate {
                tetris.rotation = (tetris.rotation + 1) % 4;
                tetris.sprite = testSprite;
            }
        }
        Direction::DOWN => {
            let mut allowMoveDown: bool = true;
            for y in 0..tetris.sprite.len() {
                for x in 0..tetris.sprite[0].len() {
                    if tetris.sprite[y][x] != 0 {
                        if tetris.y + y as i32 + 1 > 19  {
                            allowMoveDown = false
                        } else if tetris.y + y as i32 + 1 > 0{
                            if tetris.board[(tetris.y + 1 + y as i32)as usize][(tetris.x + x as i32)as usize] != 0 {
                                allowMoveDown = false
                            }
                        }
                    }
                }
            }
            if allowMoveDown {
                tetris.y += 1
            }
            else {
                spriteOnGround(tetris);
            }
        }
    }
    tetris.clock += 1;
    if tetris.clock == 3 {
        tetris.clock = -1;
        moveTetris(Direction::DOWN, tetris)
    }
}

fn rotateSprite (
    sprite: &Vec<Vec<u16>>
) -> Vec<Vec<u16>> {
    let mut output: Vec<Vec<u16>> = vec![vec![0; 4]; 4];
    for y in 0..sprite.len() {
        for x in 0..sprite[0].len() {
            output[x][sprite.len() - 1 - y] = sprite[y][x]
        }
    }
    return output
}

fn spriteOnGround (
    tetris: &mut Tetris
) {
    let mut spriteInScreenLimits: bool = true;
    for y in 0..tetris.sprite.len() {
        for x in 0..tetris.sprite[0].len() {
            if (tetris.sprite[y][x] != 0) && (y as i32 + tetris.y < 0) {
                spriteInScreenLimits = false
            }
        }
    }
    if spriteInScreenLimits {
        for y in 0..tetris.sprite.len() {
            for x in 0..tetris.sprite.len() {
                if tetris.sprite[y][x] != 0 {
                    tetris.board[(tetris.y + y as i32) as usize][(tetris.x + x as i32) as usize] = tetris.sprite[y][x]
                }
            }
        }
        newPiece(tetris);
        tetris.reward += tetris.config.piecePlaceReward;
        tetris.board.retain(|row| row.iter().sum::<u16>() as usize != 10);
        let cleared = (20 - tetris.board.len()) as u16;
        for _ in 0..cleared {
            tetris.board.insert(0, vec![0; 10]);
        }
        tetris.reward += tetris.config.lineClearReward * cleared as i32

    } else {
        gameOver(tetris);
    }
}

fn newPiece (
    tetris: &mut Tetris
) {
    tetris.x = 4;
    tetris.y = -3;
    tetris.rotation = 0;
    let mut rng = StdRng::seed_from_u64((tetris.piecesPlaced as i32 + tetris.config.seed) as u64);
    let popPiece = rng.random_range(0..tetris.bag.len());
    tetris.sprite = getSprite(tetris.bag[popPiece]);
    tetris.currentPiece = tetris.bag[popPiece];
    tetris.bag.remove(popPiece);
    if tetris.bag.len() == 0 {
        tetris.bag = vec![1, 2, 3, 4, 5, 6, 7]
    }
    tetris.piecesPlaced += 1;
}

fn gameOver (
    tetris: &mut Tetris
) {
    tetris.losses += 1;
    tetris.board = vec![vec![0; 10]; 20];
    tetris.sprite = vec![
        vec![0, 0, 0, 0],
        vec![0, 1, 0, 0],
        vec![1, 1, 1, 0],
        vec![0, 0, 0, 0]];
    tetris.currentPiece = 3;
    tetris.bag = vec![1, 2, 4, 5, 6, 7];
    tetris.rotation = 0;
    tetris.x = 4;
    tetris.y = -3;

    tetris.reward += tetris.config.gameOverReward;
    tetris.score += tetris.reward as f64 / tetris.config.attemptsPerPlayer as f64;
    tetris.reward = 0;
    tetris.piecesPlaced = tetris.losses * 100
}

fn getSprite (
    index: u16
) -> Vec<Vec<u16>>{
    match index {
            1 => return vec![
                        vec![0, 0, 0, 0],
                        vec![1, 1, 1, 0],
                        vec![1, 0, 0, 0],
                        vec![0, 0, 0, 0]],

            2 => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 1, 1, 1],
                        vec![0, 0, 0, 1],
                        vec![0, 0, 0, 0]],

            3 => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 1, 0, 0],
                        vec![1, 1, 1, 0],
                        vec![0, 0, 0, 0]],

            4 => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 0, 0, 0],
                        vec![1, 1, 1, 1],
                        vec![0, 0, 0, 0]],

            5 => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 1, 1, 0],
                        vec![0, 0, 1, 1],
                        vec![0, 0, 0, 0]],

            6 => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 1, 1, 0],
                        vec![1, 1, 0, 0],
                        vec![0, 0, 0, 0]],

            _ => return vec![
                        vec![0, 0, 0, 0],
                        vec![0, 1, 1, 0],
                        vec![0, 1, 1, 0],
                        vec![0, 0, 0, 0]],
    }
}
