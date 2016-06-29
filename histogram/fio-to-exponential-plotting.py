
#        x = range(len(self.bins))
#        pylab.rcParams.update({'font.size': 12})
#        pylab.bar(x, clats_hist)
#        pylab.ylim(0,500)
#        pylab.xticks(x, list(map(lambda x: "%.2f" % np.log2(x), self.bins)), rotation=45)
#        pylab.xlabel(r"log$_2$(clat)")
#        pylab.ylabel("frequency")
#        pylab.title("Interval=(%d - %d seconds)" % (start / 1000, end / 1000))
#        pylab.savefig("out/interval-%08d.png" % (start / self.ctx.interval))
#        pylab.close()
        #pct_error = 100 * np.abs(exact_pctiles - pctiles) / exact_pctiles


                # If we have gone past an interval, process it and remove it from the list
                #if len(inters) > 1 and sample.starts_after(i) and not i.processed:
                #    process_interval(i)
                #    pctiles.append(i.pctiles)
                #    exact_pctiles.append(i.exact_pctiles)
                
                    #inters.remove(i)
                #elif i.contains(sample):
                #    i.add(sample)
        #for i in inters:
        #    process_interval(i)
        #    pctiles.append(i.pctiles)
        #    exact_pctiles.append(i.exact_pctiles)

#    pctiles = np.array(pctiles)
#    print(pctiles)
#    y = pctiles[:,2]
#    x = range(len(y))
#    pylab.plot(x, y, '-o', c='g')
#    pylab.xlabel("interval")
#    pylab.ylabel("clat (us)")
#    pylab.legend(["95th percentile"])
#    pylab.savefig("out/95th-percentile.png")

"""
    pctiles = np.array(pctiles)
    x = list(map(lambda i: i.end / 1000, inters))
    y = np.transpose(pctiles)[2]
    print(x,y,len(x),len(y))
    pylab.scatter(x, y, c='b')
    pylab.scatter(x, np.transpose(exact_pctiles)[2], c='g')
    pylab.legend(['exp-hist w/ linear interp', 'exact'])
    pylab.show()

    #for i in inters:
    #    process_interval(i)
"""
