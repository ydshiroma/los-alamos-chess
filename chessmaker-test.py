from itertools import cycle
import time
import random

from chessmaker.chess.base import Board, Position, MoveOption
from chessmaker.chess.base import Game
from chessmaker.chess.base import Player
from chessmaker.chess.base import Square
from chessmaker.chess.pieces import Bishop
from chessmaker.chess.pieces import King
from chessmaker.chess.pieces import Knight
from chessmaker.chess.pieces import Pawn
from chessmaker.chess.pieces import Queen
from chessmaker.chess.pieces import Rook
from chessmaker.chess.results import no_kings, checkmate, stalemate, Repetition, NoCapturesOrPawnMoves
from chessmaker.clients import start_pywebio_chess_server
from chessmaker.chess.base.rule import Rule
from chessmaker.events import Event
from chessmaker.chess.base.game import AfterTurnChangeEvent
from chessmaker.chess.base.board import BeforeTurnChangeEvent
from chessmaker.chess.base.piece import BeforeGetMoveOptionsEvent
from chessmaker.chess.base.piece import BeforeGetMoveOptionsEvent
from chessmaker.chess.base.piece import AfterMoveEvent

from chessmaker.events import EventPriority
from chessmaker.events import EventPublisher, event_publisher


def _empty_line(length: int) -> list[Square]:
    return [Square() for _ in range(length)]

def get_result(board: Board) -> str:
    for result_function in [no_kings, checkmate, stalemate, Repetition(3), NoCapturesOrPawnMoves(50)]:
        result = result_function(board)
        if result:
            return result

piece_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

def create_game(**_) -> Game:
    white = Player("white")
    black = Player("black")
    turn_iterator = cycle([white, black])

    def _pawn(player: Player):
        if player == white:
            white_pawn = Pawn(white, Pawn.Direction.UP, promotions=[Rook, Queen, Knight])
            # remove option to move two squares by treating the pawn as though it's already made a move
            white_pawn._moved_turns_ago = 1
            return white_pawn
        elif player == black:
            black_pawn = Pawn(black, Pawn.Direction.DOWN, promotions=[Rook, Queen, Knight])
            black_pawn._moved_turns_ago = 1
            return black_pawn
            # return Pawn(black, Pawn.Direction.DOWN, promotions=[Rook, Queen, Knight])

    # prevent castling by treating king as though it's already moved
    def _king(player: Player):
        if player == white:
            return King(white, True)
        elif player == black:
            return King(black, True)
    
    board = Board(
            squares=[
                [Square(piece(black)) for piece in [Rook, Knight, _king, Queen, Knight, Rook]],
                [Square(_pawn(black)) for _ in range(6)],
                _empty_line(6),
                _empty_line(6),
                [Square(_pawn(white)) for _ in range(6)],
                [Square(piece(white)) for piece in [Rook, Knight, _king, Queen, Knight, Rook]],
            ],
            players=[white, black],
            turn_iterator=turn_iterator,
        )
    board.subscribe_to_all(on_any_event)
    # board.subscribe(AfterMoveEvent, on_any_event)
    board.subscribe(AfterTurnChangeEvent, play_automatic_move)
    
    game = Game(board=board,
        get_result=get_result,
    )

    return game

def on_any_event(_: Event):
    print(_)

# comment in first two lines to only console log AfterMoveEvent
# this makes it easier to track only what moves have been played and not other events
# def on_any_event(_: AfterMoveEvent):
#     print(_)
    # if _ == AfterMoveEvent(piece=Pawn (Player ("white"), Pawn.Direction.UP), move_option=MoveOption(position=Position(x=0, y=3), captures=set(), extra={})):
        # print("if condition triggered")
    # piece = AfterMoveEvent.piece
    # board = piece._board
    # square = board[Position(0, 0)]


def play_automatic_move(_: AfterTurnChangeEvent):
    if _.board.current_player.name == "black":
        has_valid_move = False
        
        while has_valid_move == False:
            pieces_iterable = _.board.get_player_pieces(_.board.current_player)
            pieces = []
            valid_moves = 0
            for piece in pieces_iterable:
                pieces.append(piece)
                valid_moves += len(piece.get_move_options())
                
            if valid_moves == 0:
                break
            
            random_num = random.randint(0, len(pieces) - 1)
            piece_to_move = pieces[random_num]
            
            move_options = piece_to_move.get_move_options()
            if len(move_options) > 0:
                time.sleep(1)
                random_move = random.randint(0, len(move_options) - 1)
                piece_to_move.move(move_options[random_move])
                has_valid_move = True
            # print(len(pieces))
            # print(random_num)
    # print(_)
    # print(_.board)
    
    
    # get random piece with available moves
    # use while loop
    # check if any moves are required?
    # or is there some way to just get all available moves for whatever color is up?
    
    # when it's black's turn, get all available moves and play one at random

    # check if there's a piece on square 1, 1; move it if so
    # square = _.board[Position(1, 1)]
    # if square.piece:
    #     time.sleep(1)
    #     piece = square.piece
    #     move_options = piece.get_move_options()
    #     piece.move(move_options[0])
        

if __name__ == "__main__":
    start_pywebio_chess_server(create_game, debug=True)