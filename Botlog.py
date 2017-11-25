import time
import datetime


class Botlog:

    def __init__(self):
        t = int(time.time())
        d = datetime.datetime.today().strftime('%Y-%m-%d')
        self.action_log = "C:\\Users\Basil\PycharmProjects\M-Fish\Logs\Actionlog-%s-%s.txt" % (d, t)
        self.data_log = "C:\\Users\Basil\PycharmProjects\M-Fish\Logs\Datalog-%s-%s.txt" % (d, t)

        # C:\Users\Basil\PycharmProjects\M-Fish\Logs\Datalog-%s-%s.txt

        fa = open(self.action_log, 'w')
        fd = open(self.data_log, 'w')

        # bot intro
        intro = '----------------------------------------------------------------------------\n' \
                '*  __  __     ___ _    _     // / /, // ,/, /, // ,/// / /, // ,/, /, // ,/*\n' \
                '* |  \/  |___| __(_)__| |_   ,, ,/, // ,/ /, //, /,/,, ,/, // ,/ /, //, /,/*\n' \
                '* | |\/| |___| _|| (_-< \' \  / ////, // ,/,/, // ///// ///  /,,/,/, ///, //*\n' \
                '* |_|  |_|   |_| |_/__/_||_| / ,,///, // ,/,/, // , / ////, // ,/,/, // ///*\n' \
                '*                            // ///  /,,/,/, ///, //, // ,/, //, ///, // ,/*\n' \
                '*--------------PREDICT RAIN. , // ,/, //, ///, // ,/// ///  /,,/,/, ///, //*\n'

        fa.write("%s\n" % intro)
        fa.write("Action Log generated on %s at %s\n" % (d, time.strftime('%H:%M:%S', time.localtime())))
        fa.close()

        fd.write("%s\n" % intro)
        fd.write("Data Log generated on %s at %s\n" % (d, time.strftime('%H:%M:%S', time.localtime())))
        fd.close()

    def log_action(self, s):
        print(s)
        f = open(self.action_log, 'a')
        f.write(">> %s\n" % s)
        f.close()

    def log_data(self, s):
        f = open(self.data_log, 'a')
        f.write("%s\n" % s)
        f.close()