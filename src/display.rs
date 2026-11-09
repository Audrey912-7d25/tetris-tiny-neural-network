use crate::data::{*};

pub fn displayTetrisState(
    tetris: &Tetris
) {
    let mut display: Vec<Vec<u16>> = vec![vec![0; 10]; 20];
    for y in 0..tetris.sprite.len() {
        for x in 0..tetris.sprite[0].len() {
            if tetris.sprite[y][x] != 0 && tetris.y + y as i32 >= 0{
                display[(tetris.y + y as i32) as usize][(tetris.x + x as i32) as usize] = 1
            }
        }
    }
    for y in 0..tetris.board.len() {
        for x in 0..tetris.board[0].len() {
            if tetris.board[y][x] != 0{
                display[y][x] = 1
            }
        }
    }
    let mut output: String = "".to_owned();
    let blackPixel: String = "\u{2591}".to_owned();
    let whitePixel: String = "\u{2588}".to_owned();
    for y in 0..20 {
        for x in 0..10 {
            if display[y][x] != 0 {
                output.push_str("\u{2591}");
                output.push_str("\u{2591}");
            }
            else {
                output.push_str("\u{2588}");
                output.push_str("\u{2588}");
            }
        }
        output.push_str("\n")
    }

    println!("{}{},{}, piece:{}, rotation:{}, reward:{}, score:{}, attempts left:{}", output, tetris.x, tetris.y, tetris.currentPiece, tetris.rotation, tetris.reward, tetris.score, tetris.config.attemptsPerPlayer - tetris.losses as i64);
}
