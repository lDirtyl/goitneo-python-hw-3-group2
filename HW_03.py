from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    def validate_phone(self):
        if not (len(self.value) == 10 and self.value.isdigit()):
            raise ValueError("Invalid format, must contain 10 digits.")


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    def validate_birthday(self):
        try:
            datetime.strptime(self.value, "%Y.%m.%d")
        except ValueError:
            raise ValueError("Invalid format. Use the YYYY.MM.DD format.")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        new_phone.validate_phone()
        self.phones.append(new_phone)

    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
            self.birthday.validate_birthday()
        else:
            raise ValueError("A birthday has already been added to this contact.")

    def remove_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                self.phones.remove(phone_obj)
                return
        raise ValueError("This phone number was not found in the phone book")

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("This phone number was not found in the phone book")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj.value
        raise ValueError("Nothing was found for this number")

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        del self.data[name]

    def find(self, name):
        return self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.now().date()
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        upcoming_birthdays = []

        for record in self.values():
            if record.birthday:
                birthday_date = (
                    datetime.strptime(record.birthday.value, "%Y.%m.%d")
                    .date()
                    .replace(year=today.year)
                )
                if today <= birthday_date:
                    upcoming_birthdays.append(record)

        return upcoming_birthdays


def input_error(error):
    def error_handler(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ValueError, IndexError):
                print(error)

        return inner

    return error_handler


def parse_birthday_input(birthday_input):
    try:
        datetime.strptime(birthday_input, "%Y.%m.%d")
        return birthday_input
    except ValueError:
        raise ValueError("Incorrect birthday format. Use the DD.MM.YYYY format.")


@input_error("Give me name and phone please.")
def add_contact(args, address_book):
    name, phone = args
    if name not in address_book:
        record = Record(name)
        record.add_phone(phone)
        address_book.add_record(record)
        return "Contact added."
    else:
        raise ValueError("Contact with this name already exists.")


@input_error("Give me name and new phone please.")
def change_contact(args, address_book):
    name, new_phone = args
    if name in address_book:
        record = address_book.find(name)
        record.edit_phone(record.phones[0].value, new_phone)
        return "Contact updated."
    else:
        raise ValueError("Contact not found.")


@input_error("Enter a name to get the phone.")
def show_phone(args, address_book):
    (name,) = args
    if name in address_book:
        record = address_book.find(name)
        return record.find_phone(record.phones[0].value)
    else:
        raise ValueError("Contact not found.")


@input_error("No contacts available.")
def show_all(address_book):
    return (
        "\n".join(str(record) for record in address_book.values())
        if address_book
        else "No contacts available."
    )


@input_error("Give me name and birthday please.")
def add_birthday(args, address_book):
    name, birthday = args
    if name in address_book:
        record = address_book.find(name)
        record.add_birthday(parse_birthday_input(birthday))
        return "Birthday added."
    else:
        raise ValueError("Contact not found.")


@input_error("Enter a name to get the birthday.")
def show_birthday(args, address_book):
    (name,) = args
    if name in address_book:
        record = address_book.find(name)
        return str(record.birthday)
    else:
        raise ValueError("Contact not found.")


def birthdays(address_book):
    upcoming_birthdays = address_book.get_birthdays_per_week()
    return (
        "\n".join(str(record) for record in upcoming_birthdays)
        if upcoming_birthdays
        else "No upcoming birthdays."
    )


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "phone":
            print(show_phone(args, address_book))
        elif command == "all":
            print(show_all(address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(address_book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
