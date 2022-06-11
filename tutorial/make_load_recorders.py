
for ln in open ('load_xfmrs.dat', mode='r').readlines():
  xfmr = ln.strip()
  print ('object recorder {')
  print ('  parent {:s};'.format(xfmr))
  print ('  file {:s}.csv;'.format(xfmr))
  print ('  interval ${INTERVAL};')
  print ('  property power_in;')
  print ('}')

