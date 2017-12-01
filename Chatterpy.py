#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Chatterpy.py: Simple, yet buggy, shared database internal chat."""

import Tkinter
import ttk
from datetime import datetime
from tkFileDialog import askopenfilename
from threading import Thread
import time
import random
import base64
import cPickle as pickle


__author__      = "Miguel Sanchez Cid"
__email__       = "mxanxez@gmail.com"
__credits__     = "Original idea by Javier Rivas"
__copyright__   = "Copyright 2017, Miguel Sanchez"
__license__     = """
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

def encode(key, msg):
    """Vigenere cipher encoding"""
    encoded_msg = []
    for i in range(len(msg)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(msg[i]) + ord(key_c)) % 256)
        encoded_msg.append(enc_c)
    return base64.urlsafe_b64encode("".join(encoded_msg))

    
def decode(key, encoded_msg):
    # """Vigenere cipher decoding"""
    decoded_message = []
    encoded_msg = base64.urlsafe_b64decode(encoded_msg)
    for i in range(len(encoded_msg)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(encoded_msg[i]) - ord(key_c)) % 256)
        decoded_message.append(dec_c)
    return "".join(decoded_message)
    

def random_name():
    """Generates a random name"""

    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"
    last_vowel=False
    
    # First uppercase letter
    if random.choice([True, False]):
        name = random.choice(consonants).upper()
    else:
        last_vowel = True
        name = random.choice(vowels).upper()
    
    # Intercalate vowels/consonants
    for i in range(random.randint(2, 5)):
        if last_vowel:
            last_vowel = False
            name += random.choice(consonants)
        else:
            last_vowel = True
            name += random.choice(vowels)

    return name
  
  
class Chatterpy:
    """Simple, yet buggy, shared database internal chat."""

    def __init__(self, chat, username=None, color=None, password=None):
        
        # Options
        self.chat = chat
        self.username  = username
        self.color  = color
        self.key  = password
        
        # TODO: clean this hack...
        self.available_colors = ["Blue", "Red", "Green", "Black", "Orange", "Purple", "Cyan", "Yellow", "Pink", "Brown", "Steel blue", "Chocolate"]
        
        # GUI options
        self.refresh_time = 1.0
        self.show_date = False
        self.show_time = False
        self.height = 20
        self.width = 40
        
        # Word to check successful decripton
        self.key_check = "Chatterpy used decription, it's not very effective..."
        
        # Si no dispone de nombre se le asignara uno de oficio
        if username is None:
            self.username = random_name()
        
        if color not in self.available_colors:
            self.color = random.choice(self.available_colors)
        
        # Ensure chat exists
        with open(self.chat, "a") as f:
            pass
            
        self.create_GUI()
        
    def update_screen(self):
        """Read all messages from the shared file and add them to the chat window"""
        
        # Rewrite everyting
        self.chatText.config(state=Tkinter.NORMAL)
        self.chatText.delete("1.0", Tkinter.END)
        
        # Get all messages from file
        msgs = []
        with (open(self.chat, "rb")) as f:
            while True:
                try:
                    msgs.append(pickle.load(f))
                except EOFError:
                    break
        
        color_count = 1
        for elem in msgs:
        
            try:
                text = ""
                
                # Decode msg
                if self.key:
                    timestamp = decode(self.key, elem[0])
                    username = decode(self.key, elem[1])
                    color = decode(self.key, elem[2])
                    msg = decode(self.key, elem[3])
                    key_check = decode(self.key, elem[4])
                else:
                    timestamp = elem[0]
                    username = elem[1]
                    color = elem[2]
                    msg = elem[3]
                    key_check = elem[4]
                
                # Check decription
                if key_check != self.key_check:
                    print "Key does not match the message encryption, ignoring message"
                    continue
                
                
                # Add timestamp if selected
                if self.show_date:
                    text += timestamp.split(" ")[0]+" "
                if self.show_time:
                    text += timestamp.split(" ")[1].split(".")[0]+" "
                    
                # Add username to message
                text += username+"> "+msg
                
                # Add to screen
                self.chatText.insert(Tkinter.END, text)
            
                # Add colors
                color_ini = str(color_count)+".0"
                color_end_int = len(username)+1
                if self.show_date:
                    color_end_int+=11
                if self.show_time:
                    color_end_int+=9
                color_end = str(color_count)+"."+str(color_end_int)
                self.chatText.tag_add(color_ini, color_ini, color_end)
                self.chatText.tag_config(color_ini, foreground=color)
                for i in range(0, len(msg.split("\n"))-1):
                    color_count+=1
            
            except Exception as e:
                print "Error in msg:", elem[1], elem[3]
                print e
             
        self.chatText.config(state=Tkinter.DISABLED)
        
        # Go to end
        self.chatText.see("end")
            
    def periodic_update(self):
        """Start a thread to periodically update chat window"""
    
        def update_thread():
            tic = time.time()
            while True:
                try:
                    if time.time()-tic > self.refresh_time:
                        tic = time.time()
                        self.update_screen()
                except Exception as e:
                    print e
                    break
        t = Thread(target=update_thread, args=())
        t.daemon = True#if True thread dies with the program
        t.start()
            
    def send_msg(self, msg):
        """Dump a message tuple to the shared file"""
        
        # Encode msg
        if self.key:
            coded_timestamp = encode(self.key, str(datetime.now()))
            coded_username = encode(self.key, self.username)
            coded_color = encode(self.key, self.color)
            coded_msg = encode(self.key, msg)
            coded_key_check = encode(self.key, str(self.key_check))
        else:
            coded_timestamp = str(datetime.now())
            coded_username = self.username
            coded_color = self.color
            coded_msg = msg
            coded_key_check = self.key_check
            
        # Write to file
        with open(self.chat, "ab") as f:
            pickle.dump((coded_timestamp, coded_username, coded_color, coded_msg, coded_key_check), f)
            
        # Update screen
        self.update_screen()
        
    def send_msg_button_pressed(self, event=None):
        """Send message and clear writing field"""
    
        # Get message
        msg = self.sendText.get("1.0", Tkinter.END)
        
        # If called with Enter, remove last \n
        if event is not None:
            msg = "\n".join([elem for elem in msg.split("\n")[:-1]])
        self.send_msg(msg)
        
        # Clear field
        self.sendText.delete("1.0", Tkinter.END)
            
    def delete_chat(self):
        """Clear shared file"""

        with open(self.chat, "w") as f:
            pass

    def about(self):
        """
        Chatterpy: Simple, yet buggy, shared database internal chat.
        author    = "Miguel Sanchez Cid"
        email     = "mxanxez@gmail.com"
        credits   = "Original idea by Javier Rivas"
        copyright = "Copyright 2017, Miguel Sanchez"
        license = "GNU General Public License"
        """
            
        toplevel = Tkinter.Toplevel(self.root)
        label0 = Tkinter.Label(toplevel, text="\n     Chatterpy", font=("Helvetica", 9, "bold"))
        label0.grid(row=0, column=1, padx=1, sticky = "sw")
        label1 = ttk.Label(toplevel, text=  "     Simple, yet buggy, shared "
                                            "\n     database internal chat.\n     "
                                            "\n     Copyright 2017 Miguel Sanchez"
                                            "\n     GNU General Public License"
                                            "\n     mxanxez@gmail.com"
                                            "\n      ")
        label1.grid(row=1, column=1, padx=1, sticky = "s")
        close_aboutButton = ttk.Button(toplevel, text="     Ok     ", command = toplevel.destroy)
        close_aboutButton.grid(row=2, column=1)
        label2 = ttk.Label(toplevel, text=" ")
        label2.grid(row=3, column=1, padx=1, sticky = "s")
                    
    def apply_options(self, chat, username, password, color, show_date, show_time, refresh_time, height, width, window_to_destroy):
        """Set class configuration data"""
        
        try:
            self.username = username
            self.key = password
            self.chat = chat
            
            # Ensure chat exists
            with open(self.chat, "a") as f:
                pass
            
            if color in self.available_colors:
                self.color = color
                
            self.show_date = show_date
            self.show_time = show_time
            self.refresh_time = float(refresh_time)
            self.height = int(height)
            self.width = int(width)
            self.chatText.config(height = self.height, width = self.width)
            self.sendText.config(width = self.width-10)
            
        except Exception as e:
            print e
            
        self.update_screen()
        window_to_destroy.destroy()
        
    def options(self):
        """Launch pop-up option window"""
        
        nrow=0
        toplevel = Tkinter.Toplevel(self.root)
        toplevel.attributes('-topmost', True)
        toplevel.resizable(False, False)
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        def reroll_username():
            self.username = random_name()
            username_field.delete(0, Tkinter.END)
            username_field.insert(0, self.username)
        label = Tkinter.Label(toplevel, text="Username:  ")
        username_field_button = ttk.Button(toplevel, text=" Username: ", command= reroll_username)
        username_field_button.grid(row=nrow, column=1, sticky="e")
        username_field = ttk.Entry(toplevel, width = 25)
        username_field.grid(row=nrow, column=2, sticky="w")
        username_field.delete(0, Tkinter.END)
        username_field.insert(0, self.username)         
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        label = Tkinter.Label(toplevel, text="Password:  ")
        label.grid(row=nrow, column=1, sticky="e")
        password_field = ttk.Entry(toplevel, width = 25)
        password_field.grid(row=nrow, column=2, sticky="w")
        if self.key is not None:
            password_field.delete(0, Tkinter.END)
            password_field.insert(0, self.key) 
        else:
            password_field.delete(0, Tkinter.END)
            password_field.insert(0, "") 
            
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        label = Tkinter.Label(toplevel, text="Color:  ")
        label.grid(row=nrow, column=1, sticky="e")
        color_var = Tkinter.StringVar()
        dropdown_color_field = ttk.OptionMenu(toplevel, color_var, self.color, *self.available_colors)
        dropdown_color_field.config(width=20)
        dropdown_color_field.grid(row=nrow, column=2, sticky="w")
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        def set_chat_button():
            File_name= askopenfilename(title="Choose chat")
            chat_field.delete(0, Tkinter.END)
            chat_field.insert(0, File_name)
        chat_field_button = ttk.Button(toplevel, text=" Chat: ", command= set_chat_button)
        chat_field_button.grid(row=nrow, column=1, sticky="e")
        chat_field = ttk.Entry(toplevel, width = 25)
        chat_field.grid(row=nrow, column=2, sticky="w")
        chat_field.delete(0, Tkinter.END)
        chat_field.insert(0, self.chat) 
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        show_date_var = Tkinter.IntVar()
        show_date_var.set(self.show_date)
        show_date_button = ttk.Checkbutton(toplevel, text = "Show message date", variable = show_date_var)
        show_date_button.grid(row=nrow, column=2, sticky="w")
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        show_time_var = Tkinter.IntVar()
        show_time_var.set(self.show_date)
        show_time_button = ttk.Checkbutton(toplevel, text = "Show message time", variable = show_time_var)
        show_time_button.grid(row=nrow, column=2, sticky="w")
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1)
        
        nrow+=1
        label = Tkinter.Label(toplevel, text="Refresh time:  ")
        label.grid(row=nrow, column=1, sticky="e")
        refresh_field = ttk.Entry(toplevel, width = 25)
        refresh_field.grid(row=nrow, column=2, sticky="w")
        refresh_field.insert(Tkinter.END, self.refresh_time) 
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        label = Tkinter.Label(toplevel, text="Height:  ")
        label.grid(row=nrow, column=1, sticky="e")
        height_field = ttk.Entry(toplevel, width = 25)
        height_field.grid(row=nrow, column=2, sticky="w")
        height_field.insert(Tkinter.END, self.height) 
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        label = Tkinter.Label(toplevel, text="Width:  ")
        label.grid(row=nrow, column=1, sticky="e")
        width_field = ttk.Entry(toplevel, width = 25)
        width_field.grid(row=nrow, column=2, sticky="w")
        width_field.insert(Tkinter.END, self.width) 
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        clear_chat = ttk.Button(toplevel, text="  Delete chat history  ", command= self.delete_chat)
        clear_chat.grid(row=nrow, column=2)
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=1, padx=1)
        
        nrow+=1
        close_aboutButton = ttk.Button(toplevel, text="     Ok     ", command =  lambda: self.apply_options(chat_field.get(), username_field.get(), password_field.get(), color_var.get(), show_date_var.get(), show_time_var.get(), refresh_field.get(), height_field.get(), width_field.get(), toplevel) )
        close_aboutButton.grid(row=nrow, column=2)
        
        nrow+=1
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=0, sticky = "s")
        label = ttk.Label(toplevel, text=" ")
        label.grid(row=nrow, column=100, padx=1, sticky = "s")
        
    def create_GUI(self):
        """Launch main window"""
        
        self.root = Tkinter.Tk()
        self.root.title("Chatterpy")
        self.root.resizable(False, False)

        self.root.bind('<Return>', self.send_msg_button_pressed)

        # Menu bar
        self.menu_bar = Tkinter.Menu(self.root)
        self.file_menu = Tkinter.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Options", command=self.options)
        self.file_menu.add_command(label="About", command=self.about)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        
        #Add everything to menu
        self.menu_bar.add_cascade(label="Menu", menu=self.file_menu)
        
        # display the menu
        self.root.config(menu=self.menu_bar)
        
        
         # Frame for chatText
        self.txtFrame = Tkinter.Frame(self.root, borderwidth=1, relief="sunken")
        # Chat Text
        self.chatText = Tkinter.Text(self.txtFrame, height = self.height, width = self.width)
        self.chatText.insert(Tkinter.END, '') 
        self.chatText.config(state=Tkinter.DISABLED)
        
         # Scrollbar for chatText
        self.vscroll = Tkinter.Scrollbar(self.txtFrame, orient=Tkinter.VERTICAL, command=self.chatText.yview)
        self.chatText['yscroll'] = self.vscroll.set
        self.chatText.grid(row=0, column=0)
        self.vscroll.grid(row=0, column=1,sticky="ns")
        self.txtFrame.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        
        # Send Text
        self.sendText = Tkinter.Text(self.root, height = 2, width = self.width-10)
        self.sendText.grid(row=4, column=1, padx=10, pady=10)
        self.sendText.insert(Tkinter.END, '') 
        self.checkButton = ttk.Button(self.root, text=" Send! ", command= self.send_msg_button_pressed)
        self.checkButton.grid(row=4, column=2, padx=10, pady=10)
        
        # Pop-up options window
        # self.options()
        
        # Periodically loads chat
        self.periodic_update()
        
        self.root.mainloop()
        
if __name__=="__main__":

    # Chat database
    default_database = "chat.db"
    default_username = None
    default_color = None
    default_password = None
    chat = Chatterpy(default_database, default_username, default_color, default_password)