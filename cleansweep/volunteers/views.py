from ..plugin import Plugin
from flask import (flash, request, render_template, redirect, url_for, abort)
from ..models import db, Place, Member
from .. import forms
from ..voterlib import voterdb
from . import signals, notifications, audits, stats

plugin = Plugin("volunteers", __name__, template_folder="templates")

def init_app(app):
    plugin.init_app(app)


@plugin.place_view("/volunteers", permission="view-volunteers")
def volunteers(place):
    return render_template("volunteers.html", place=place)


@plugin.place_view("/volunteers/add", methods=['GET', 'POST'], permission="write")
def add_volunteer(place):
    form = forms.AddVolunteerForm(place, request.form)
    if request.method == "POST" and form.validate():
        if form.voterid.data:
            voterid = form.voterid.data
            voter = voterdb.get_voter(voterid=voterid, trynew=True)
            p = voter.get_place()
        else:
            p = Place.find(key=form.place.data)
        volunteer = p.add_member(
            name=form.name.data, 
            email=form.email.data or None,
            phone=form.phone.data or None,
            voterid=form.voterid.data or None)
        db.session.commit()
        signals.add_new_volunteer.send(volunteer)
        flash(u"Added {} as volunteer to {}.".format(form.name.data, p.name))
        return redirect(url_for(".volunteers", key=place.key))
    return render_template("add_volunteer.html", place=place, form=form)


@plugin.route("/people/<id>-<hash>")
def profile(id, hash):
    m = Member.find(id=id)
    if not m or m.get_hash() != hash:
        abort(404)
    return render_template("profile.html", person=m)