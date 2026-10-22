class Turn:
    def __init__(self, chanel):
        self.chanel = chanel
        self.next = None
        self.prev = None
        
class TurnRing:
    def __init__(self):
        self.current_turn:Turn = None
        
    def insert_at_end(self, chanel):
        new_turn = Turn(chanel)
        
        if self.current_turn is None:
            self.current_turn = new_turn
            new_turn.next = new_turn
            new_turn.prev = new_turn
        else:
            # points to the prev turn before current
            last = self.current_turn.prev
            #now the next one is the current turn [current] -> [last] -> [new]
            last.next = new_turn
            #now next turn for the new one is the current
            new_turn.next = self.current_turn
            #the previous is last 
            new_turn.prev = last
            #the previous turn of current is the new one
            self.current_turn.prev = new_turn
    
    def advance (self):
        if self.current_turn is not None:
            self.current_turn = self.current_turn.next
            
    def find (self, chanel):
        if self.current_turn is None:
            return None
        current = self.current_turn
        while True:
            if current.chanel == chanel:
                return current
            current = current.next
            if (current is self.current_turn):
                return None
    
    def current_chanel(self):
        if self.current_turn is None:
            return None
        return self.current_turn.chanel
    
    def is_empty(self):
        return self.current_turn is None
    
    def remove_turn(self, chanel):
        turn = self.find(chanel)
        if turn is None:
            return False
        # if there is only one turn
        if turn.next is turn:
            self.current_turn = None
        else:
            # [prev]-[turn]-[next]
            turn.prev.next = turn.next
            turn.next.prev = turn.prev
            # if turn equals to current turn cursor
            if turn is self.current_turn:
                self.current_turn = turn.next
        
        return True
    
    def to_list(self):
        chanels = []
        if self.is_empty():
            return None
        # add the current pointer
        chanels.append(self.current_turn.chanel)
        # initialize the current pointer to the next one of current
        current:Turn = self.current_turn.next
        while current != self.current_turn:
            # append the current chanel
            chanels.append(current.chanel)
            current = current.next
        return chanels