import re
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self._is_valid_phone(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    def _is_valid_phone(self, value):
        return re.fullmatch(r'\d{10}', value) is not None

class Birthday(Field):
    def __init__(self, value):
        if not self._is_valid_birthday(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def _is_valid_birthday(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        if not isinstance(record, Record):
            raise TypeError("Only Record instances can be added.")
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                next_birthday = birthday_date.replace(year=today.year)
                
                if today <= next_birthday <= today + timedelta(days=7):
                    if next_birthday.weekday() >= 5:
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))
                    upcoming_birthdays.append({"name": record.name.value, "birthday": next_birthday.strftime('%d.%m.%Y')})

        return upcoming_birthdays

    def __str__(self):
        if self.data:
            return "\n".join(str(record) for record in self.data.values())
        else:
            return "No contacts found."

# Декоратор для обробки помилок вводу
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return str(e)
    return wrapper

# Обробники команд
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    return "Contact not found."

@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return str(record)
    return "Contact not found."

@input_error
def show_all_contacts(_, book):
    return str(book)

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{record.name.value}'s birthday is on {record.birthday.value}"
    return "Contact or birthday not found."

@input_error
def show_upcoming_birthdays(_, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join([f"{entry['name']}: {entry['birthday']}" for entry in upcoming_birthdays])

# Парсинг вводу
def parse_input(user_input):
    return user_input.strip().split()

# Основна функція бота
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(show_upcoming_birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
