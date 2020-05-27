# gret_notes

Project for personalized notes.

## Test-site on the pythoneverywhere server:

http://gret.pythonanywhere.com

## Idea:

 App for notes with option to make it fast and ergonomic.
 Options to build up old notes, with fast recognizing, what note you want to expand.
 Sharing content, to make possibility of working in groups.
 Connecting both options - to make possible providing system of fast information exchange, within teams.

## Features:

* **Notes**
    * [x] Basic notes (new/view/update/delete functions)
    * [x] Tagging - primal organization / search feature
        * [x] Search notes by tags
        * [ ] Links for fast adding and deleting note's tags
    * [ ] Grouping - more organization for your notes (to allow sharing the whole group)
    * [ ] Pinup - fast links to most important/urgent cases
        * [ ] List by set up expiration time or priority

* **User / Teamwork:**
    * [x] User authorization
    * [ ] Basic user groups, group owner interface
    * [ ] Sharing notes with other users 
        * [ ] Sharing any content with users / groups
    * [ ] Dividing notes into sections with different privileges / owners for each section
    * [ ] Prioritizing notes / flags / statuses / votes

* **Other:**
    * [ ] Checklists / Next step lists (stand alone from notes)
        * [ ] Checklists / Next step lists - build into notes
    * [ ] Build in system to choose storage place (including local, or local network secure storage for internal purposes)

## DB model:

![Image od DB model](https://i.ibb.co/Q6b5Tj1/DB-model.png)

## Sources of knowledge:

* Started with: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
* https://ondras.zarovi.cz/sql/demo/ - DB modeling online
* https://docs.python.org/3.6/
    * https://flask.palletsprojects.com
    * https://www.sqlalchemy.org
    * https://wtforms.readthedocs.io
* https://stackoverflow.com - fixes and minor features (like JS)
* https://realpython.com
* https://hackersandslackers.com
