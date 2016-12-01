import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt


def isFloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('file_name', help='The csv file to plot')
	args = parser.parse_args()
	_filename = args.file_name
	windows = []
	thou = []
	thou_err = []
	lb = []
	lb_err = []
	lp = []
	lp_err = []
	with open(_filename, newline='') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			if not isFloat(row[0]):
				continue
			windows.append(int(row[1]))
			thou.append(float(row[2]))
			thou_err.append(float(row[3]))
			lb.append(float(row[4]))
			lb_err.append(float(row[5]))
			lp.append(float(row[6]))
			lp_err.append(float(row[7]))

	fig, ax1 = plt.subplots()
	fig.subplots_adjust(right=0.75)
	ax1.errorbar(windows, thou, yerr=thou_err, color='blue')
	ax1.set_xlim([2, 4096])
	ax1.set_xscale('log', basex=2)
	ax1.set_xlabel('Window size (packets)')
	ax1.set_ylabel('Throughput (KB/s)')
	for tl in ax1.get_yticklabels():
		tl.set_color('b')

	ax2 = ax1.twinx()
	ax2.set_xlim([2, 4096])
	ax2.errorbar(windows, lb, yerr=lb_err, color='red')
	ax2.set_ylabel('Lost Bytes')
	for tl in ax2.get_yticklabels():
		tl.set_color('r')

	ax3 = ax1.twinx()
	ax3.set_xlim([2, 4096])
	ax3.spines['right'].set_position(('axes', 1.2))
	ax3.set_frame_on(True)
	ax3.patch.set_visible(False)
	ax3.errorbar(windows, lp, yerr=lp_err, color='green')
	ax3.set_ylabel('Lost Packets')
	for tl in ax3.get_yticklabels():
		tl.set_color('g')

	plt.show()
