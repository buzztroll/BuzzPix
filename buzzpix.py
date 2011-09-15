import ConfigParser
import glob
import sys
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def parse_options(directory):
    conf_file = "%s/.buzzpix.ini" % (directory)
    config = ConfigParser.SafeConfigParser()
    config.read(conf_file)
    email_info = EmailRecipientInfo()
    
    email_info.smtp_server = config.get("email", "smtp")
    email_info.to_list = config.get("email", "to").split(",")
    email_info.subject = config.get("email", "subject")
    email_info.message = config.get("email", "message")
    email_info.username = config.get("email", "username")
    email_info.password = config.get("email", "password")
    email_info.from_addr = config.get("email", "from")

    return email_info


class EmailRecipientInfo(object):
    to_list = None
    from_addr = None
    subject = None
    message = None
    smtp_server = None
    username = None
    password = None

def earliest_file(search_dir):
    files = filter(os.path.isfile, glob.glob(search_dir  + "/*"))
    files.sort(key=lambda x: os.path.getmtime(x))
    if files:
        return files[0]
    return None

def send_it_native(filename, email_recip):
    msg = MIMEMultipart()
    msg['Subject'] = email_recip.subject
    msg['From'] = email_recip.from_addr
    msg['To'] = email_recip.from_addr
    msg.preamble = email_recip.message

    fp = open(filename, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP(email_recip.smtp_server)
    s.starttls()
    s.login(email_recip.username, email_recip.password)
    to_list = [email_recip.from_addr] + email_recip.to_list
    s.sendmail(email_recip.from_addr, to_list, msg.as_string())
    s.quit()

    return True


def main(argv=sys.argv[1:]):
    filename = earliest_file(argv[0])
    if not filename:
        print "ADD MORE PICTURES!"
        return 1

    email_recip = parse_options(argv[0])

    attachments = filename

    try:
        rc = send_it_native(attachments, email_recip)
        if rc:
            print "sent file %s to %s" % (attachments, email_recip.to_list)
            os.unlink(filename)
        else:
            print "failed to send file %s to %s" % (email_recip.to_list, email_recip.to_list)

        return rc
    except Exception, ex:
        print ex
        raise


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
