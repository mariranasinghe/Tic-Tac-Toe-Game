class Protocols:
    class Response:
        NICKNAME = "protocol.request_nickname"
        BOARD_UPDATE = "protocol.board_update"
        TURN = "protocol.player_turn"
        OPPONENT_TURN = "protocol.opponent_turn"
        SYMBOL_ASSIGN = "protocol.symbol_assign"
        START = "protocol.start"
        OPPONENT = "protocol.opponent"
        WINNER = "protocol.winner"
        DRAW = "protocol.draw"
        OPPONENT_LEFT = "protocol.opponent_left"
        
    class Request:
        MOVE = "protocol.move"
        NICKNAME = "protocol.send_nickname"
        LEAVE = "protocol.leave"
