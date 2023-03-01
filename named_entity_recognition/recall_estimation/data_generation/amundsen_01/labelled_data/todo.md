1. Reformat this directory so that we can do consolidation of multiple labellers
2. Separate the final output files into separate directory so that it is easy to update the benchmark.
3. Remove all intermediate files that are not needed to be stored
   - keep all original labelstudio input files
   - keep the files that are copied to the benchmark
4. Update .gitignore so that other intermediate files in this directory are ignored 
