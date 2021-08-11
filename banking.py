import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
conn.commit()


class BankingSystem:

    def __init__(self):
        self.main_interface()

    def main_interface(self):
        self.user_input = input("\n1. Create an account\n2. Log into account\n0. Exit\n")
        if self.user_input == "1":
            self.create_account()
        elif self.user_input == "2":
            self.login_account()
        elif self.user_input == "0":
            print("\nBye!")

    def create_account(self):
        self.card_num = "400000" + str(random.randint(0, 999999999)).zfill(9)
        self.luhn_checksum(self.card_num)
        self.card_num += self.last_digit
        self.pin = str(random.randint(0, 1000)).zfill(4)
        cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (self.card_num, self.pin))
        conn.commit()
        print(f"\nYour card has been created\nYour card number:\n{self.card_num}\nYour card PIN:\n{self.pin}\n")
        self.main_interface()

    def login_account(self):
        input_card_num = input("\nEnter your card number:\n")
        input_pin = input("Enter your PIN:\n")
        cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (
        input_card_num,))
        try:
            self.record = list(cur.fetchone())
            if input_pin == self.record[1]:
                print("\nYou have successfully logged in!")
                self.login_interface()
            else:
                print("\nWrong card number or PIN!")
                self.main_interface()
                self.record = None
        except TypeError:
            print("\nWrong card number or PIN!")
            self.main_interface()
            self.record = None

    def login_interface(self):
        self.user_input = input("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
        if self.user_input == "1":
            print(f"Balance: {self.record[2]}")
            self.login_interface()
        elif self.user_input == "2":
            income = int(input("\nEnter income:\n"))
            self.record[2] += income
            cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.record[2], self.record[0]))
            conn.commit()
            print("Income was added!")
            self.login_interface()
        elif self.user_input == "3":
            self.transfer_num = input("\nTransfer\nEnter card number:\n")
            self.do_transfer()
            self.login_interface()
        elif self.user_input == "4":
            cur.execute("DELETE FROM card WHERE number = ?", (self.record[0],))
            conn.commit()
            print("\nThe account has been closed!")
            self.main_interface()
            self.record = None
        elif self.user_input == "5":
            print("\nYou have successfully logged out!\n")
            self.main_interface()
            self.record = None
        elif self.user_input == "0":
            print("\nBye!")
            self.record = None

    def luhn_checksum(self, fifteen_digit_string):
        multiply_odd_two = [int(fifteen_digit_string[i]) * 2 for i in range(0, 15, 2)]
        substract_nine = [num - 9 for num in multiply_odd_two if num > 9]
        num_less_nine = [num for num in multiply_odd_two if num <= 9]
        even_digit = [int(fifteen_digit_string[i]) for i in range(1, 15, 2)]
        total_sum = sum(substract_nine) + sum(num_less_nine) + sum(even_digit)
        if total_sum % 10 == 0:
            self.last_digit = "0"
        else:
            checksum_digit = str(10 - (total_sum % 10))
            self.last_digit = checksum_digit

        return self.last_digit

    def do_transfer(self):
        if self.transfer_num[15] != self.luhn_checksum(self.transfer_num[:15]):
            print("Probably you made a mistake in the card number. Please try again!")

        elif self.transfer_num == self.record[0]:
            print("You can't transfer money to the same account!")

        else:
            cur.execute("SELECT number FROM card")
            list_of_card_num = cur.fetchall()

            if (self.transfer_num,) in list_of_card_num:
                cur.execute("SELECT number, balance FROM card WHERE number = ?", (self.transfer_num,))
                transfer_record = list(cur.fetchone())
                money = int(input("Enter how much money you want to transfer:\n"))

                if money > self.record[2]:
                    print("Not enough money!")

                else:
                    self.record[2] -= money
                    cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.record[2], self.record[0]))
                    conn.commit()
                    transfer_record[1] += money
                    cur.execute("UPDATE card SET balance = ? WHERE number = ?",
                                (transfer_record[1], transfer_record[0]))
                    conn.commit()
                    print("Success!")

            else:
                print("Such a card does not exist.")


BankingSystem()
conn.close()