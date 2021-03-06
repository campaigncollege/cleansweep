from . import signals
from ..audit import record_audit

@signals.committee_add_member.connect
def on_committee_add_member(committee, member, role):
    record_audit(
        action="committee.add-member",
        timestamp=None,
        place=committee.place,
        person=member,
        data=dict(
            committee=committee.dict(),
            member=member.dict(),
            role=role.dict()))

@signals.committee_remove_member.connect
def on_committee_remove_member(committee, member, role):
    record_audit(
        action="committee.remove-member",
        timestamp=None,
        place=committee.place,
        person=member,
        data=dict(
            committee=committee.dict(),
            member=member.dict(),
            role=role.dict()))

@signals.new_committee_structure.connect
def on_new_committee_structure(committee_type):
    record_audit(
        action="committee-structure.new",
        timestamp=None,
        place=committee_type.place,
        person=None,
        data=dict(committee_type=committee_type.dict()))

@signals.committee_structure_modified.connect
def on_committee_structure_modified(committee_type, old):
    record_audit(
        action="committee-structure.edit",
        timestamp=None,
        place=committee_type.place,
        person=None,
        data=dict(
            committee_type=committee_type.dict(),
            old=old
            ))