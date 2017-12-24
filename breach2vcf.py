#!/usr/bin/env python

import argparse
import os
import sys
try:
   import vobject
except ImportError:
   sys.stderr.write('Please install vobject with pip or pip2 (pip2 install vobject)\n')
   sys.exit(1)


class Email(object):
   def __init__(self, fullname, email, datafiles, output_dir):
      self.fullname = fullname
      self.address = email
      self.initials = self.address[:2]
      if not datafiles.get(self.initials):
         self.initials = self.address[:3]
      self.logfile = None
      self.output_dir = output_dir

   def match(self, line):
      if self.address not in line:
         return
      if not self.logfile:
         self.logfile = open(os.path.join(self.output_dir, self.fullname + '.txt'), 'a')
      self.logfile.write(line)
      print self.fullname, line[:-1]

   def done(self):
      if self.logfile:
         self.logfile.close()


class DataFile(object):
   def __init__(self, dirpath, filename):
      self.filepath = os.path.join(dirpath, filename)
      if 'symbol' in self.filepath:
         raise ValueError
      elements = self.filepath.split('/')
      start = elements.index('data') + 1
      self.initials = ''.join(elements[start:])

   def match(self, emails):
      print '%s: %d potential matches' % (self.filepath, len(emails))
      with open(self.filepath) as datafile:
         for line in datafile.readlines():
            for email in emails:
               email.match(line)


def parse_contacts(vcffile, datafiles, output_dir):
   vcf_contacts = vobject.readComponents(open(vcffile).read())
   emails = {}
   for vcf_contact in vcf_contacts:
      if 'email' not in vcf_contact.contents:
         continue
      name = vcf_contact.contents['fn'][0].value
      for email in vcf_contact.contents['email']:
         email = Email(name, email.value, datafiles, output_dir)
         if email.initials:
            emails.setdefault(email.initials, []).append(email)
   os.mkdir(output_dir)
   return emails


def find_datafiles(dirpath):
   datafiles = {}
   for root, _, filenames in os.walk(dirpath):
      for filename in sorted(filenames):
         try:
            datafile = DataFile(root, filename)
            datafiles[datafile.initials] = datafile
         except ValueError:
            continue
   return datafiles


def main():
   parser = argparse.ArgumentParser()
   parser.add_argument('vcf', metavar='VCF FILE', nargs=1)
   parser.add_argument('--data-dir', default='data')
   parser.add_argument('--output-dir', default='logs')
   args = parser.parse_args()
   datafiles = find_datafiles(args.data_dir)
   emails = parse_contacts(args.vcf[0], datafiles, args.output_dir)
   for initials in sorted(datafiles):
      matching_emails = emails.get(initials)
      if matching_emails:
         datafiles[initials].match(matching_emails)
         for email in matching_emails:
            email.done()


if __name__ == "__main__":
   sys.exit(main())
