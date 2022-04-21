rm IF*.txt
cp testbench_IF.mt0 IF_modelanswer.txt
sed 's/\./0/g' IF_modelanswer.txt > IF_model1.txt
sed 's/[0-9]*e\-[0-9]*/0/g' IF_model1.txt > IF_model2.txt
sed 's/\-0/0/g' IF_model2.txt > IF_model3.txt
sed 's/[1][0-9]*/1/g' IF_model3.txt > IF_results.txt
diff IF_results.txt model_IF.txt -w > diff.txt
if [[ -s diff.txt ]]; then
echo "Failed"
else
echo "Passed"
fi;
