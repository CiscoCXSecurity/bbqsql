import bbqsql
import unittest



#We don't need all the output....
bbqsql.settings.QUIET = True
test_data = ['Strange women lying in ponds distributing swords is no basis for a system of government. Supreme executive power derives from a mandate from the masses, not from some farcical aquatic ceremony.', 'Three rings for the Elven kings under the sky, seven for the Dwarf lords in their halls of stone, nine for the mortal men doomed to die, one for the Dark Lord on his dark throne, in the land of Mordor where the shadows lie. One ring to rule them all, one ring to find them, one ring the bring them all, and in the darkness bind them. In the land of Mordor where the shadows lie.', 'Im sorry, Dave. Im afraid I cant do that.', 'Spock. This child is about to wipe out every living thing on Earth. Now, what do you suggest we do....spank it?', 'With great power there must also come -- great responsibility.', 'If you cant take a little bloody nose, maybe you oughtta go back home and crawl under your bed. Its not safe out here. Its wondrous, with treasures to satiate desires both subtle and gross; but its not for the timid.', 'Five card stud, nothing wild. And the skys the limit', 'If you think that by threatening me you can get me to do what you want... Well, thats where youre right. But -- and I am only saying that because I care -- theres a lot of decaffeinated brands on the market that are just as tasty as the real thing.', 'Were all very different people. Were not Watusi. Were not Spartans. Were Americans, with a capital A, huh? You know what that means? Do ya? That means that our forefathers were kicked out of every decent country in the world. We are the wretched refuse. Were the underdog.', 'If Im not back in five minutes, just wait longer.', 'Im going to give you a little advice. Theres a force in the universe that makes things happen. And all you have to do is get in touch with it, stop thinking, let things happen, and be the ball.', 'WE APOLOGIZE FOR THE INCONVENIENCE', 'Some days, you just cant get rid of a bomb!', 'Bill, strange things are afoot at the Circle K.', 'Invention, my dear friends, is 93% perspiration, 6% electricity, 4% evaporation, and 2% butterscotch ripple.', 'Didja ever look at a dollar bill, man? Theres some spooky shit goin on there. And its green too.', 'Alright, alright alright.', 'Heya, Tom, its Bob from the office down the hall. Good to see you, buddy; howve you been? Things have been alright for me except that Im a zombie now. I really wish youd let us in.', 'Never argue with the data.', 'Oooh right, its actually quite a funny story once you get past all the tragic elements and the over-riding sense of doom.']

class TestBlindRequester(unittest.TestCase):
    def test_exploit(self):
        bh = bbqsql.BooleanBlindSQLi()
        results = bh.run(concurrency=100)
        self.assertEqual(results,test_data)


if __name__ == "__main__":
    unittest.main() 
