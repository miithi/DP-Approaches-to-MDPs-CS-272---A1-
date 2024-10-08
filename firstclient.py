import asyncio
import random
import datetime
import csv
# ++++++++++++++++++++++++++++++++++++++++++++++++++
# You must not change anything other than:
# SERVER_IP variable
# SPORT variable
# __mylogic function (Do not change the function name)
# ++++++++++++++++++++++++++++++++++++++++++++++++++
SERVER_IP = '35.193.27.191'
SPORT = 10019 # check your port number
class MyAgent:
    def __init__(self) -> None:
        # initial state is always (0,0)
        self.current_state = (0,0)
        

    def __is_valid(self, d:str) -> bool:
        """Check if the reply contains valid values
        Args:
        d (str): decoded message
        Returns:
        bool:
        1. If a reply starts with "200", the message contains the valid
        next state and reward.
        2. If a reply starts with "400", your request had an issue. Error
        messages should be appended after it.
        """

        if d.split(',')[0] == '200':
            return True
        return False
    
    def __parse_msg(self, d:str) -> list:
        """ Parse the message and return the values (new state (x,y), reward r, and 
        if it reached a terminal state)
        Args:
        d (str): decoded message
        Returns:
        new_x: the first val of the new state
        new_y: the second val of the new state
        r: reward
        terminal: 0 if it has not reached a terminal state; 1 if it did reach
        """
        reply = d.split(',')
        new_x = int(reply[1])
        new_y = int(reply[2])
        r = int(reply[3])   
        terminal = int(reply[4])
        return new_x, new_y, r, terminal

    def __mylogic(self, reward: int) -> int:
        """Implement your agent's logic to choose an action. You can use the
        current state, reward, and total reward.
        Args:
        reward (int): the last reward received
        Returns:
        int: action ID (0, 1, 2, or 3)
        """
        print(f'State = {self.current_state}, reward = {reward}')

        current_x, current_y = self.current_state
        
             
        if current_y < 9:  # Hypothetical target y-coordinate
            return 0  # Move up
        elif current_x < 4: #hypothetical target x-coordinate
            return 2  # Move right
        else:
        # Choose a random action if none of the above conditions are met
            return random.choice([0, 1, 2, 3])

        
        # If the reward is negative or zero, try a different action
        #if state_x > state_y:
            #action = random.choice([1, 3])
        #else:
            #action = random.choice([0, 2])

        #if reward == 0:
            #action = random.choice([0, 1, 2, 3])
    
    # Return the chosen action
        #return action
# your logic goes here
        #a = random.choice([0,1,2,3]) # random policy
# An action id should be returned
        #return a

    async def runner(self):
        #"""Play the game with the server, following your logic in __mylogic() until
        #it reaches a terminal state, reached step limit (5000), or receives an invalid
        #reply. Print out the total reward. Your goal is to come up with a logic that always
        #produces a high total reward.
        #"""
        total_r = 0
        reward = 0
        STEP_LIMIT = 600
        step = 0

        # Open the CSV file in append mode ('a') to add new runs
        with open('experiment_runs.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
        
        # Optionally write the header only if the file is empty
            if step == 0:  # Only add headers for the first run
                writer.writerow(["Step", "Action", "Reward", "New State", "Total Reward"])

            while True:
                print(f'step {step}')
            
                # Get the action based on your logic
                a = self.__mylogic(reward)

                # Send the current state and action to the server
                message = f'{self.current_state[0]},{self.current_state[1]},{a}'
                is_valid, new_x, new_y, reward, terminal = await self.__communicator(message)

                # If invalid response or step limit, terminate with total_r = 0
                total_r += reward
                if (not is_valid) or (step >= STEP_LIMIT):
                    total_r = 0
                    print('There was an issue. Ignore this result.')
                    break 
                elif terminal:
                    print('Normally terminated.')
                    break

                # Log the step, action, reward, and new state into the CSV
                writer.writerow([step, a, reward, (new_x, new_y), total_r])

                # Update the current state and increment the step
                self.current_state = (new_x, new_y)
                step += 1

        # Print the final total reward at the end of the run
        print(f'total reward = {total_r}')


        while True:
            # Set an action based on your logic
            print(f'step {step}')
            a = self.__mylogic(reward)
            # Send the current state and action to the server
            # And receive the new state, reward, and termination flag
            message = f'{self.current_state[0]},{self.current_state[1]},{a}'
            is_valid, new_x, new_y, reward, terminal = await self.__communicator(message)
            
            # If the agent (1) reached a terminal state
            # (2) received an invalid reply,
            # or (3) reached the step limit (STEP_LIMIT steps),
            # Terminate the game (Case (2) and (3) should be ignored in the results.)
            total_r += reward
            if (not is_valid) or (step >= STEP_LIMIT):
                total_r = 0
                print('There was an issue. Ignore this result.')
                break 
            elif terminal:
                print('Normally terminated.')
                break
            self.current_state = (new_x, new_y)
            step += 1
        print(f'total reward = {total_r}') 

    async def __communicator(self, message): 
        """Send a message to the server
        Args:
        message (str): message to send (state and action)
        Returns:
        list: validity, new state, reward, terminal
        """
        reader, writer = await asyncio.open_connection(SERVER_IP, SPORT)
        print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()
        data = await reader.read(512)
        print(f'Received: {data.decode()!r} at {datetime.datetime.now()}')
        results = (-1,-1,-1,-1) # dummy results for failed cases
        is_valid = self.__is_valid(data.decode())
        if self.__is_valid(data.decode()):
            results = self.__parse_msg(data.decode()) 
        # print('Close the connection')
        writer.close()
        await writer.wait_closed()
        return (is_valid, *results)
ag = MyAgent() # type: ignore
asyncio.run(ag.runner())