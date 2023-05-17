
from YTShortDriver import YTShortDriver
from time import sleep
import pandas as pd


driver = YTShortDriver(use_virtual_display=False)
driver.login("nicholas_nelson_609@youtubeaudit.com", "Erty1234!")


# # profile = "hadiaskari23"
# # query = "abortion"

# # def training(n):
# #     likes = 0
# #     shorts = []
# #     while likes < n:
# #         sleep(2)
# #         # get short
# #         short = driver.get_current_short()
# #         shorts.append(short.to_dict())
# #         if classify(query, short.description):
# #             print("Relevant. Watching...")
# #             sleep(30)
# #             driver.positive_signal()
# #             shorts[-1]['liked'] = True
# #             likes += 1
# #         # move to next short
# #         driver.next_short()
# #     return pd.DataFrame(shorts)

# # def testing(n):
# #     shorts = []
# #     for _ in range(n):
# #         sleep(2)
# #         # get short
# #         short = driver.get_current_short()
# #         shorts.append(short.to_dict())
# #         # move to next short
# #         driver.next_short()
# #     return pd.DataFrame(shorts)

# # def intervention(n):
# #     dislikes = 0
# #     shorts = []
# #     while dislikes < n:
# #         sleep(2)
# #         # get short
# #         short = driver.get_current_short()
# #         shorts.append(short.to_dict())
# #         if classify(query, short.description):
# #             print("Relevant. Downvoting...")
# #             driver.negative_signal()
# #             shorts[-1]['unliked'] = True
# #             dislikes += 1
# #         # move to next short
# #         driver.next_short()
# #     return pd.DataFrame(shorts)

# # if __name__ == '__main__':
# #     # load the driver
# #     driver = YTShortDriver(use_virtual_display=False, profile_dir='profiles/%s' % profile)
    
# #     # load the driver
# #     driver.goto_homepage()

# #     # wait for user setup
# #     input("Start?")

# #     # training phase 2
# #     # print("Entering training phase 2")
# #     # driver.goto_shorts()
# #     # training_phase_2 = training(25)

# #     # # testing phase 1
# #     # print("Entering testing phase 1")
# #     # driver.goto_shorts()
# #     # testing_phase_1 = testing(100)

# #     # # intervention phase 1
# #     # print("Entering intervention phase 1")
# #     # driver.goto_shorts()
# #     # intervention_phase = intervention(10)

# #     # # testing phase 2
# #     # print("Entering testing phase 2")
# #     # driver.goto_shorts()
# #     # testing_phase_2 = testing(100)

# #     # # write results
# #     # training_phase_2.to_csv('results/%s-training-phase-2.csv' % profile, index=False)
# #     # testing_phase_1.to_csv('results/%s-testing-phase-1.csv' % profile, index=False)
# #     # intervention_phase.to_csv('results/%s-intervention-phase.csv' % profile, index=False)
# #     # testing_phase_2.to_csv('results/%s-testing-phase-2.csv' % profile, index=False) 