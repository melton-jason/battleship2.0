"""
Program Name: singleplayer.py

Description:
This program contains the game loop and logic for running a multiplayer version of a Pygame-based Battleship game. It handles the placement of ships for both Player 1 and Player 2, manages turns, updates the game board with hits and misses, and determines when the game is over. The game operates in two-player mode, alternating between the players until one player wins by sinking all of the opponent's ships.

Inputs:
- pos: Mouse position for determining player actions on the grid.
- player1ships, player2ships: Arrays containing the lengths of the ships for Player 1 and Player 2.
- player1placedShips, player2placedShips: 2D arrays representing the positions of the ships for both players.
- player1hits, player2hits: Arrays tracking the hits made by each player.
- player1misses, player2misses: Arrays tracking the misses made by each player.

Output:
- Displays updates to the game board, including ship placements, hits, misses, and win/loss messages.
- Alternates between Player 1 and Player 2 turns, showing the appropriate updates after each move.

Code Sources:
- Pygame documentation for event handling and drawing.
- Based on previously implemented grid and logic for Battleship game in Pygame.

Author: Zai Erb

Creation Date: September 2, 2024
"""


from matplotlib.pyplot import pause
import pygame
import sys
import copy
import add_text
import place_ships
import get_ships_num
import battleship
import easy
import medium
import hard

def run(difficulty = None):
    print("singleplayer")
    arrays = get_ships_num.get_ships(battleship.player1ships, battleship.player2ships, battleship.SCREEN, battleship.player1placedShips, battleship.player2placedShips)
    battleship.player1ships = arrays[0]
    battleship.player2ships = arrays[1]
    battleship.player1placedShips = arrays[2]
    battleship.player2placedShips = arrays[3]
    ship_hit = False
    
    if difficulty == "easy":
        ai = easy.EasyAI()
    elif difficulty == "medium":
        ai = medium.MediumAI()
    elif difficulty == "hard":
        ai = hard.HardAI()

    #run while the game is not ended
    while not battleship.gameover:
        pos = pygame.mouse.get_pos()
        
        if not battleship.player1ready:
            place_ships.placePlayer1Ships(battleship.SCREEN, battleship.player1ships, battleship.player1placedShips, battleship.player1ShipBoard)
            battleship.player1ready = True
            battleship.copyPlayer1placedShips = copy.deepcopy(battleship.player1placedShips)
        
        if not battleship.player2ready:
            ai.placeShips(battleship.SCREEN, battleship.player2ships, battleship.player2placedShips, battleship.player2ShipBoard)
            battleship.player2ready = True
            battleship.copyPlayer2placedShips = battleship.createShallowCopy(battleship.player2placedShips)
            if (difficulty == 'hard'):
                enemy_ships = []
                for ship in battleship.player1placedShips:
                    for rect in ship:
                        x = battleship.getRow(battleship.player1ShipBoard, rect)
                        y = battleship.getCol(battleship.player1ShipBoard, rect)
                        print(f'x: {x}')
                        print(f'y: {y}')
                        enemy_ships.append((x, y))
                    ai.targets = enemy_ships
                    print(ai.targets)

            print(battleship.player2placedShips)
        # add text saying battleship and add rows and cols
        add_text.add_text(battleship.SCREEN, 'Battleship')
        add_text.add_labels_targets(battleship.SCREEN)
        # if it is player 1 turn, say that and print their boards
        if battleship.player1Turn:
            add_text.add_text(battleship.SCREEN, 'Your Turn')
            battleship.printShipBoard(battleship.player1ShipBoard, battleship.player1placedShips, battleship.player2hits)
            battleship.printBoard(battleship.player1TargetBoard, battleship.player1hits, battleship.player1misses)
            add_text.add_labels_middle(battleship.SCREEN)
            add_text.add_labels_ships(battleship.SCREEN)

        keys = pygame.key.get_pressed()
        event = pygame.event.poll()
        
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            pygame.mixer.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
         # if it is player 1 turn, check for a hit and checkForCollision will handle all the logic for updating hits and misses
            if battleship.player1Turn:
                battleship.ACHANNEL.play(battleship.CAUDIO) #sound effect for firing cannon
                pygame.time.delay(1000) #Short delay to allow for a little bit of tension
                played = battleship.checkForCollision(battleship.player1TargetBoard, battleship.player2ShipBoard, pos, battleship.player1hits, battleship.player1misses, battleship.player2placedShips, battleship.copyPlayer2placedShips, battleship.player1BlastRadius)
                if played: 
                    # if they made a valid move, update the boards
                    battleship.printShipBoard(battleship.player1ShipBoard, battleship.player1placedShips, battleship.player2hits)
                    battleship.printBoard(battleship.player1TargetBoard, battleship.player1hits, battleship.player1misses)
                    pygame.display.update()
                    # check for a sunk ship
                    shipsSunk = battleship.shipsSunk(battleship.copyPlayer2placedShips)
                    # if they sunk a ship, check if all ships are sunk
                    if shipsSunk > 0:
                        battleship.player1BlastRadius += shipsSunk
                        add_text.add_text(battleship.SCREEN, 'You sunk a ship!')
                        pygame.display.update()
                        ended = battleship.gameIsOver(battleship.copyPlayer2placedShips)
                        if ended:
                            battleship.gameover = True
                            add_text.add_text(battleship.SCREEN, 'You won!')
                            pygame.display.update()
                            pygame.time.wait(2000)
                            add_text.ask_play_again(battleship.SCREEN)
                    pause(1)
                    print(battleship.gameover)
                    if not battleship.gameover:
                        add_text.add_black_screen(battleship.SCREEN)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        pygame.event.clear()
                    battleship.player1Turn = False
                
                if not battleship.gameover:
                    add_text.add_text(battleship.SCREEN, 'AI is making a move...')
                    pygame.display.update()
                    pygame.time.delay(1000)
                    previous_hits_length = len(battleship.player2hits)
                    row, col = ai.make_move(ship_hit)
                    played = ai.checkForCollision(battleship.player2TargetBoard, battleship.player1ShipBoard, row, col, battleship.player2hits, battleship.player2misses, battleship.player1placedShips, battleship.copyPlayer1placedShips, battleship.player2BlastRadius)
                    while not played:
                        row, col = ai.make_move(ship_hit)
                        played = ai.checkForCollision(battleship.player2TargetBoard, battleship.player1ShipBoard, row, col, battleship.player2hits, battleship.player2misses, battleship.player1placedShips, battleship.copyPlayer1placedShips, battleship.player2BlastRadius)

                    if difficulty == 'medium':
                        if len(battleship.player2hits) > previous_hits_length:
                            print("Ship hit on last turn.")
                            ship_hit = True
                            ai.update_last_hit(row, col)
                    if played:
                        battleship.printBoard(battleship.player2TargetBoard, battleship.player2hits, battleship.player2misses)
                        pygame.display.update()
                        shipsSunk = battleship.shipsSunk(battleship.copyPlayer1placedShips)
                        if shipsSunk > 0:
                            battleship.player2BlastRadius += shipsSunk
                            add_text.add_text(battleship.SCREEN, 'AI sunk a ship!')
                            ship_hit = False
                            pygame.display.update()
                            ended = battleship.gameIsOver(battleship.copyPlayer1placedShips)
                            if ended:
                                battleship.gameover = True
                                add_text.add_text(battleship.SCREEN, 'AI won!')
                                pygame.display.update()
                                pygame.time.wait(2000)
                                add_text.ask_play_again(battleship.SCREEN)
                        pause(1)
                        if not battleship.gameover:
                            add_text.add_black_screen(battleship.SCREEN)
                            pygame.display.update()
                            pygame.time.wait(2000)
                            pygame.event.clear()
                        battleship.player1Turn = True

        pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    battleship.gameover = False
                    battleship.player1Turn = True
                    battleship.player1ready = False
                    battleship.player2ready = False
                    battleship.player1hits = []
                    battleship.player1misses = []
                    battleship.player1BlastRadius = 0
                    battleship.player2hits = []
                    battleship.player2misses = []
                    battleship.player1placedShips = []
                    battleship.player2placedShips = []
                    battleship.player1ships = []
                    battleship.player2ships = []
                    battleship.player2BlastRadius = 0
                    battleship.SCREEN.fill((0,0,0))
                    pygame.display.update()
                    run(difficulty)
                elif event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()

