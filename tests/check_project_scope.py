from app.models import *
from database import reset
import pdb

reset()


p=Project(name="test")
w=Word(word="foo")
w2=Word(word="bar")
w3=Word(word="mar")
s=Sentence(text="foo bar")

Project.active_project = p

s.add_word(w)

print(w.sentences)

p2=Project(name="test2")
s2=Sentence(text="foo mar")

Project.active_project = p2

s2.add_word(w)

print(w.sentences)

print("\n==============\n")

se=Sequence(sequence="foo bar")
se2=Sequence(sequence="foo mar")

Project.active_project = p

se.add_word(w)

print(w.sequences)
print(w.sentences)

Project.active_project = p2

se2.add_word(w)

print(w.sequences)
print(w.sentences)

print("\n==============\n")

d=Dependency(governor=w, dependent=w2)

Project.active_project = p

s.add_dependency(d)

print(d.sentences)
print(w.sequences)
print(w.sentences)

Project.active_project = p2

s2.add_dependency(d)

print(d.sentences)
print(w.sequences)
print(w.sentences)

print("\n==============\n")

Project.active_project = p

s.add_sequence(se)

print(se.sentences)
print(d.sentences)
print(w.sequences)
print(w.sentences)

Project.active_project = p2

s2.add_sequence(se)

print(se.sentences)
print(d.sentences)
print(w.sequences)
print(w.sentences)

print("\n==============\n")

s2.add_sequence(se, project=p)

print(se.sentences)

Project.active_project = p

print(se.sentences)
