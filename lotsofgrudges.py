from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Grudget, Base, Grudge, User

engine = create_engine('sqlite:///grudgebucketwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#DumbDebby user
User1 = User(name="Lorena Bobbett", email="lbobbett@hotmail.com",
             picture='https://randomuser.me/api/portraits/women/71.jpg')
session.add(User1)
session.commit()

# Grudge Bucket for Strangers

grudget1 = Grudget(user_id=1,name="Husbands Like John")
session.add(grudget1)
session.commit()

grudge1 = Grudge(user_id=1,name="Jerks who drink", description="These jerks use alcohol to escape their issues and then use their power over you",
                     processed="True" , takeaway="Avoid dating alcholics", grudget=grudget1)

session.add(grudge1)
session.commit()


grudge2 = Grudge(user_id=1,name="Whenever I want", description="Jerk who think women are at their mercy",
                     processed="True", takeaway="That mofo will never hurt another women again.", grudget=grudget1)

session.add(grudge2)
session.commit()


grudge3 = Grudge(user_id=1,name="Creepy neighbor", description="While in college on a late night a neighbor flashed his schlong at me as I was putting my key in the door to my apt",
                     processed="False",takeaway="Unprocessed, I still hate that guy for doing that to me.", grudget=grudget1)

session.add(grudge3)
session.commit()



# Grudge Bucket for Bosses
grudget2 = Grudget(user_id=1,name="Bosses")

session.add(grudget2)
session.commit()


grudge4 = Grudge(user_id=1,name="The non solicited editor", description="I once had a boss, who would spend hours editing my powerpoint presentations, because he didn't think I knew proper english",
                     processed="True" ,takeaway="Never be like him, always assume the best of people", grudget=grudget2)

session.add(grudge4)
session.commit()


grudge5 = Grudge(user_id=1,name="The AssHole", description="I had this boss that loved belitting people to the point of tears. Even when we attempted to warn him when he was going off the deep end he always ended up hurting his team to the point of tears.",
                     processed="True" ,takeaway="Life is too short to put up with that type of bullshit", grudget=grudget2)

session.add(grudge5)
session.commit()

# Grudge Bucket for Coworkers
grudget3 = Grudget(user_id=1,name="CoWorkers")

session.add(grudget3)
session.commit()


grudge6 = Grudge(user_id=1,name="Take Credit for your work", description="I like to have treats in the office, chocolate, mints, etc. This was a new tradition I wanted to establish at the office. I heard an exec inquire about what an excellent idea that was and a coworker take credit for a treat jar that was at my desk, funded with chocolate of my own money",
                     processed="True", takeaway="low blow, let them have it. Truth will come to light", grudget=grudget3)

session.add(grudge6)
session.commit()


grudge7 = Grudge(user_id=1,name="BrownNoser", description="This person has no idea what they are doing professionally, but are very effective at establishing strong political relationships and talking about sports",
                     processed="True", takeaway="Always carry Poopari, to spray it on said coworker, and step up your sports game!", grudget=grudget3)

session.add(grudge7)
session.commit()


print "all grudges loaded, woot woot"
# print "----> grudges_by(user.id):"
# query = session.query(Grudge)
# for _row in query.all():
#     print(_row.name, _row.description, _row.processed,_row.takeaway)
