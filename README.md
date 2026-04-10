## Norges Bank Investment Management Voting Records
### About
NBIM votes at annual shareholder meetings. Five days before each meeting, NBIM publishes its voting intentions.
When NBIM votes against the board’s recommendation, it provides an explanation. Voting instructions are available from 2013. Explanations are available from 1 April 2020.

NBIM publishes its voting instructions via an [API](https://www.nbim.no/en/responsible-investment/voting/our-voting-records/api-access-to-our-voting/). You have to apply for an APIkey and use it on your GET requets.

### Scripts
Since there is a day limit of  5000 API calls, I've created scripts for data crawling:
* `src\company_list_request.py` asks '/v1/ds/companies' end for company names
* `src\company_info_query.py` collects all company's meetings ids and dates from '/v1/query/company/' end
* `src\meetings_info_query.py` collects the votes for every question from the meetings ('/v1/query/meeting/' end)

### Data
The following repo contains table data with voting records gathered from the API. 
The `data` folder contains the resulting datasets. The (`data\meetings_info.csv`)[data\meetings_info.csv] is the final CSV file with all voting records up to January 7, 2026. The file has 16 columns and 1436265 entries (every row/entry is a vote for a separate ,eeting question). The fund doesn't provide output interpretation (the API output format - nested dictionary) so the explanaition may be not 100% correct. Columns:
* companyId - the fund's inner id number (not very useful)
* companyName - the company name
* companyTicker - stock ticker symbol
* isin - company's international securities identification number
* meetingDate - shareholders meeting date
* meetingId - shareholders meeting id
* meetingType - shareholders meeting type
* itemOnAgendaId - numerical question identificator (internal, i guess)
* managementRec  - issuer's management recommendation for voting
* proponent - the source of the recommendation
* proposalNumber - most likely the number in bulletin (not sure)
* proposalSequence - most likely the number in bulletin (not sure)
* proposalText - text of the proposal
* voteInstruction - fund's vote
* voterRationale - rational if against
* globalVotingGuidelines - link to the guidelines if applicable

The voting results are also available on the following fund's (webpage)[https://www.nbim.no/en/responsible-investment/voting/our-voting-records/] separtely ffor every company (you need either the name or the ticker).

The (`data\consolidated_equity_holdings.csv`)[data\consolidated_equity_holdings.csv] is the consolidated CSV file with all funds equity holdings at the end of each year. The `equity_holdings` folder contains investment's market value in equity original files (each file for one year) for 1999-2025 years (as of 31.12) from [fund's website](https://www.nbim.no/en/investments/all-investments). The (consolidation script)[src\consolidate_equity_holdings.py].

The `examples` folder contains some EXCEL examples from the `meetings_info.csv` file:
- (`first_100_entries.xlsx`)[examples\first_100_entries.xlsx] - first 100 entries (sorted by region) in EXCEL format
- (`votes_against.xlsx`)[examples\votes_against.xlsx] - is the collection of all AGAINST votes on the boards' proposals.

Some company names were not processed, and their names are saved in the (`data/failed_names.csv`)[data\failed_names.csv] file. Currently I'm trying to fugure out how to solve it using the ticker quiery. 

### Disclosure 1.0
This is an educational project and by no means should it be regarded as fully correct. No reliance should be placed on this information or its accuracy. 

### Disclosure 2.0
The below is provided as FYI notes from the email NBIM sent with the API key:

The following resources are available via API:
- /v1/ds/tickers
- /v1/ds/companies
- /v1/query/ticker/<string:ticker>
- /v1/query/company/<string:companyname>
- /v1/query/companyid/<string:companyid>
- /v1/query/isin/<string:isin>
- /v1/query/meeting/<string:meetingid>

Disclaimer and conditions:

This API contains certain information as to the voting intentions of Norges Bank in its role as manager of the Government Pension Fund Global. This disclosure is provided to promote transparency as to Norges Bank’s engagement with investee companies, and in view of its approach to responsible investing. Norges Bank’s voting intention is an internal decision and has not been agreed with any third party. Please note the following:

* This disclosure is provided for information purposes only. It does not constitute advice and should not be taken as a recommendation or an instruction on any matter, including whether any relevant third party should buy, sell or retain shares, or how any third party should exercise any voting rights they may have. Any person who wishes to obtain advice should seek this from a professional adviser. This disclosure is not a proxy solicitation and is not intended to influence the vote of other shareholders.
* No reliance should be placed on this information or its accuracy, and Norges Bank accepts no responsibility or liability for any action taken or not taken on the basis of this information. Any relevant third party should form their own views based on their own analysis of the relevant facts and circumstances.
* To be clear, Norges Bank has no duty of care in respect of any third party who decides to view this disclosure, which shall be done entirely at their own risk.
* Any information in this disclosure is subject to change without notice. In particular, be aware that Norges Bank’s intentions and the holdings of the Government Pension Fund Global may change over time and, to the extent permitted by applicable law, Norges Bank disclaims any responsibility to update this information as a result of such changes or for any other reason.
* Securities lending or other activity may mean that the votes cast by Norges Bank are significantly different than its economic or published holding of shares, or significantly different from its holding at the date of this disclosure. No assumption should be made or reliance placed on the number of votes that will be cast.
* Norges Bank is not subject to any prohibition on securities lending, trading or other activity as a result of this disclosure at any point prior to or after the publication of this disclosure.
* Norges Bank has no duty of care in respect of any third party who decides to use this API. Norges Bank may suspend, disable or withdraw access to the API at any time or remove the API entirely. Norges Bank will not be responsible for any loss, damage, costs, expenses or other liability of any third party resulting from the suspension, disabling or withdrawal of access via the API or the removal of the API. Norges Bank will not be liable for any inability to access the API, costs incurred by any third party, or any losses, lost profits or damages of any kind arising out of or in connection with the use of the API. Norges Bank makes no warranty of any kind with respect to this API, whether express, implied, statutory or otherwise, including any warranty that the API will be compatible with any third-party’s software, system or other service. All API access is the responsibility of the user and it is acknowledged that the API is provided on an “AS IS” basis without warranties of any kind. Norges Bank does not warrant or represent that access via the API will be delivered free of any inaccuracies, interruptions, delays, omissions or errors (“Faults”), or that any Faults will be corrected. Norges Bank will not be liable for any loss or damages resulting from any such Faults.
This disclaimer shall be read and interpreted independently of any other disclaimer on this website.