from ..plugin import Plugin
from ..models import db, Member
from .models import CommitteeRole, CommitteeType
from flask import (flash, request, render_template, redirect, url_for, abort)
from . import forms
from . import signals, notifications, audits


plugin = Plugin("committees", __name__, template_folder="templates")


def init_app(app):
    plugin.init_app(app)


@plugin.place_view("/committees", permission="read")
def committees(place):
    return render_template("admin/committees.html", place=place)


@plugin.place_view("/committees/<slug>", methods=["GET"], permission="read")
def view_committee(place, slug):
    committee = place.get_committee(slug)
    if not committee:
        abort(404)
    return render_template("view_committee.html", place=place, committee=committee)


@plugin.place_view("/committees/<slug>/edit", methods=["GET", "POST"], permission="write")
def edit_committee(place, slug):
    committee = place.get_committee(slug)
    if not committee:
        abort(404)

    if request.method == "POST":
        action = request.form.get('action')
        if action == "add":
            role_id = request.form['role']
            email = request.form['email']
            role = CommitteeRole.query.filter_by(id=role_id).first()
            member = Member.find(email=email)
            committee.add_member(role, member)
            db.session.commit()
            signals.committee_add_member.send(committee, member=member, role=role)
            flash("{} has been added as {}".format(email, role.role))
        elif action == 'remove':
            role_id = request.form['role']
            email = request.form['email']
            role = CommitteeRole.query.filter_by(id=role_id).first()
            member = Member.find(email=email)
            committee.remove_member(role, member)
            signals.committee_remove_member.send(committee, member=member, role=role)
            db.session.commit()
            flash("{} has been removed as {}".format(email, role.role))

    return render_template("edit_committee.html", place=place, committee=committee)

@plugin.place_view("/committee-structures/new", methods=['GET', 'POST'], permission="write")
def new_committee_structure(place):
    form = forms.NewCommitteeForm(place)
    if request.method == "POST" and form.validate():
        committee_type = CommitteeType.new_from_formdata(place, form)
        db.session.commit()
        signals.new_committee_structure.send(committee_type)

        flash("Successfully defined new committee {}.".format(form.slug.data), category="success")
        return redirect(committee_type.url_for(".view_committee_structure"))
    else:
        return render_template("new_committee_structure.html", place=place, form=form)

@plugin.place_view("/committee-structures", permission="write")
def committee_structures(place):
    return render_template("committee_structures.html", place=place)

@plugin.place_view("/committee-structures/<level>.<slug>", permission="write")
def view_committee_structure(place, slug, level):
    committee_type = CommitteeType.find(place, slug, level=level)
    return render_template("view_committee_structure.html", place=place, committee_type=committee_type)

@plugin.place_view("/committee-structures/<level>.<slug>/edit", methods=['GET', 'POST'], permission="write")
def edit_committee_structure(place, slug, level):
    form = forms.NewCommitteeForm(place)
    committee_type = CommitteeType.find(place, slug, level=level)
    if request.method == "POST" and form.validate():
        d1 = committee_type.dict()
        form.save(committee_type)
        db.session.commit()
        flash("Successfully updated {}.".format(committee_type.name), category="success")
        signals.committee_structure_modified.send(committee_type, old=d1)
        return redirect(committee_type.url_for(".view_committee_structure"))
    else:
        if request.method != 'POST':
            form.load(committee_type)
        return render_template("edit_committee_structure.html", place=place, committee_type=committee_type, form=form)
