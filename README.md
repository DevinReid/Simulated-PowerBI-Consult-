This is a project I did in collaboration with a PowerBI consulting firm, to showcase and stregthen my skills in DAX and Report Building.

The project adhered to these best practices:

No iteration/filtering over the Sales table – All filtering is applied to virtual tables only.
No calculated columns – All calculations are dynamic and within the measure itself.
No calculated tables – Other than the DateTable, no calculated tables are used.
No added columns to dimensions or virtual tables – All calculations stay within the context of the measure.

Iterating over a fact table like our sales table, can create some major performance issues, especially if the customer is working with a larger database, or planning to scale to one in the future.

Calculated columns can also negatively impact performance. They increase the file size of the dataset, add unnecessary clutter, and lack the flexibility of filter context, which is kind of the entire reason for PowerBi's design, leveraging filter context to deliver fast, scalable, and dynamic results in ways previous software struggled to.


Simulated_consult_v1.pbix contains the final solution

I built the database in python to test. 