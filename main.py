from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    sender: str
    content: str
    timestamp: datetime

    def __str__(self):
        return f"{self.sender}: {self.content}"

    @property
    def is_image(self):
        return self.content.startswith("afbeelding weggelaten")

    @property
    def is_sticker(self):
        return self.content.startswith("sticker weggelaten")

    @property
    def is_video(self):
        return self.content.startswith("video weggelaten")

    @property
    def is_audio(self):
        return self.content.startswith("audio weggelaten")

    @property
    def is_document(self):
        return self.content.startswith("document weggelaten")

    @property
    def is_gif(self):
        return self.content.startswith("GIF weggelaten")

    @property
    def is_location(self):
        return self.content.startswith("Locatie: ")

    @property
    def is_contact(self):
        return self.content.startswith("Visitekaartje weggelaten")

    @property
    def is_changed_group_image(self):
        return self.content.endswith(
            "heeft de groepsafbeelding gewijzigd") or "U hebt de groepsafbeelding gewijzigd" in self.content

    @property
    def is_changed_security_code(self):
        return self.content.endswith("is gewijzigd. Tik voor meer informatie.")

    @property
    def is_person_added(self):
        return self.content.endswith(
            f" toegevoegd") or "is deelnemer geworden via de uitnodigingslink van deze groep" in self.content or "U bent deelnemer geworden via de uitnodigingslink van deze groep" in self.content

    @property
    def is_person_removed(self):
        return self.content.endswith(
            f"heeft {self.sender} verwijderd") or "heeft u verwijderd" in self.content or f"{self.sender} heeft de groep verlaten" in self.content or "U hebt de groep verlaten" in self.content

    @property
    def is_changed_group_topic(self):
        return "heeft het onderwerp gewijzigd naar" in self.content or "heeft de groepsomschrijving gewijzigd" in self.content

    @property
    def is_added_to_community(self):
        return "heeft deze groep en de bijbehorende deelnemers aan de community" in self.content

    @property
    def is_removed_from_community(self):
        return "heeft deze groep verwijderd uit de community" in self.content or (
                "heeft de community" in self.content and self.content.endswith("gedeactiveerd"))

    @property
    def is_admin_approval_enabled(self):
        return "Nieuwe deelnemers aan deze groep moeten door beheerders worden goedgekeurd." in self.content or "kan vragen om deelname aan deze groep door een bericht naar groepsbeheerders te versturen." in self.content

    @property
    def is_admin_approval_disabled(self):
        return "heeft beheerdersgoedkeuring voor deelname aan deze groep uitgeschakeld" in self.content

    @property
    def is_changed_group_name(self):
        return "heeft het onderwerp gewijzigd naar" in self.content or "U hebt het onderwerp gewijzigd naar" in self.content

    @property
    def is_changed_phone_number(self):
        return "heeft een nieuw telefoonnummer. Tik om een bericht te sturen of om het nieuwe nummer toe te voegen." in self.content

    @property
    def is_disappearing_message_disabled(self):
        return "heeft berichten met vervaldatum uitgeschakeld" in self.content

    @property
    def is_waiting_for_message(self):
        return self.content.startswith("Wachten op deze berichten...") or self.content.startswith(
            "Wachten op dit bericht.")

    @property
    def is_group_created(self):
        return self.content.startswith("U hebt deze groep aangemaakt") or self.content.endswith(
            "heeft deze groep aangemaakt") or "Berichten en gesprekken worden end-to-end versleuteld. Niemand buiten deze chat kan ze lezen of beluisteren, zelfs WhatsApp niet." in self.content

    @property
    def is_system_message(self):
        return (
                self.is_image
                or self.is_changed_group_image
                or self.is_changed_security_code
                or self.is_person_added
                or self.is_person_removed
                or self.is_changed_group_topic
                or self.is_added_to_community
                or self.is_removed_from_community
                or self.is_admin_approval_enabled
                or self.is_admin_approval_disabled
                or self.is_changed_group_name
                or self.is_changed_phone_number
                or self.is_disappearing_message_disabled
                or self.is_waiting_for_message
                or self.is_group_created
        )

    @property
    def is_regular_chat(self):
        return (
                not self.is_system_message
                and not self.is_sticker
                and not self.is_video
                and not self.is_audio
                and not self.is_document
                and not self.is_gif
                and not self.is_location
                and not self.is_contact
                and not self.is_deleted
        )

    @property
    def is_deleted(self):
        return self.content.startswith("Dit bericht is verwijderd.") or self.content.startswith(
            "U hebt dit bericht verwijderd.")

    @property
    def start_with_hashtag(self):
        return self.content.startswith("#")

    @property
    def breaks_rules(self):
        words = self.content.split(" ")
        return any([not w.startswith("#") for w in words])


def parse_message_file(message_file):
    messages = []
    with open(message_file, "r") as f:
        for line in f:
            # Messages have the following format: [dd-mm-yy hh:mm:ss] Sender: Content
            # We can split the line on the first colon to get the sender and content
            # The timestamp is between square brackets
            try:
                line = line.replace("‎", "")
                timestamp, sender_content = line.split("]", 1)
                sender, content = sender_content.split(":", 1)
                timestamp = timestamp[1:]
                if timestamp.startswith("["):
                    timestamp = timestamp[1:]
                sender = sender.strip()
                content = content.strip()
                timestamp = datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")
                messages.append(Message(sender, content, timestamp))
            except ValueError:
                continue
    return messages


def _order_by_senders(messages):
    senders = defaultdict(int)
    for message in messages:
        senders[message.sender] += 1
    return dict(sorted(senders.items(), key=lambda x: x[1], reverse=True))


def order_by_senders(messages, n=None):
    if n is None:
        return _order_by_senders(messages)
    return _order_by_senders(messages)[:n]


def most_recent_message_for_sender(messages):
    most_recent = {}
    for message in messages:
        most_recent[message.sender] = max(message.timestamp, most_recent.get(message.sender, message.timestamp))
    return dict(sorted(most_recent.items(), key=lambda x: x[1], reverse=True))


def main():
    messages = parse_message_file("_chat.txt")

    images = list(filter(lambda m: m.is_image, messages))
    print(f"Found {len(images)} images")
    most_active_image_senders = order_by_senders(images)
    print(f"Most active image senders: {most_active_image_senders}")

    regular_chats = list(filter(lambda m: m.is_regular_chat, messages))
    print(f"Found {len(regular_chats)} regular chat messages")
    most_active_senders = order_by_senders(regular_chats)
    print(f"Most active regular chat senders: {most_active_senders}")

    broken_rules = list(filter(lambda m: m.breaks_rules, regular_chats))
    print(f"Found {len(broken_rules)} messages that break the rules")
    most_active_rule_breakers = order_by_senders(broken_rules)
    print(f"Most active rule breakers in chat messages: {most_active_rule_breakers}")

    most_recent_selfies = most_recent_message_for_sender(images)
    print(f"Most recent selfie for each sender: {most_recent_selfies}")

    for person, most_recent_selfie in reversed(most_recent_selfies.items()):
        days_ago = (datetime.now() - most_recent_selfie).days
        print(f"Most recent selfie for {person}: {days_ago} days ago")

    print("Done")


if __name__ == "__main__":
    main()
