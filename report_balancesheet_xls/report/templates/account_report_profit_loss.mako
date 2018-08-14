## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}

            .list_table .act_as_row {
                margin-top: 10px;
                margin-bottom: 10px;
                font-size:10px;
            }
        </style>
    </head>
    <body>
        <%!

        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%def name="format_amount(amount, display_option=None)">
            <%
            output = amount
            if display_option == 'normal':
                output = amount
            elif display_option == 'round':
                output = u"%.0f" % round(amount)
            elif display_option == 'kilo':
                if amount:
                    output = u"%.2fK" % (amount / 1000,)
            %>
            ${output}
        </%def>

        <%setLang(user.lang)%>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell text-bold" style="font-weight:bold">${_('Chart of Account')}</div>
                <div class="act_as_cell" style="font-weight:bold">${_('Fiscal Year')}</div>
                <div class="act_as_cell" style="font-weight:bold">
                    %if filter_form == 'filter_date':
                        ${_('Dates')}
                    %else:
                        ${_('Periods')}
                    %endif
                </div>
                <div class="act_as_cell" style="font-weight:bold">${_('Target Moves')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ chart_account.name }</div>
                <div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell">
                    ${_('From:')}
                    %if filter_form == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <div class="act_as_cell">${ target_move }</div>
            </div>
        </div>

        

        <div class="act_as_table list_table" style="margin-top: 20px;">

            <div class="act_as_thead">
                <div class="act_as_row labels">
                    ## account name
                    <div class="act_as_cell" style="width: 80px;">${_('Account')}</div>
                    %if debit_credit:
                        ## debit
                        <div class="act_as_cell amount" style="width: 30px;">${_('Debit')}</div>
                        ## credit
                        <div class="act_as_cell amount" style="width: 30px;">${_('Credit')}</div>
                    %endif
                    ## balance
                    <div class="act_as_cell amount" style="width: 30px;">
                    %if filter == 'filter_no' or not fiscalyear:
                        ${_('Balance')}
                    %else:
                        ${_('Balance %s') % (fiscalyear.name,)}
                    %endif
                    </div>

                    %if enable_filter:
                        <div class="act_as_cell amount" style="width: 30px;">${_(label_filter)}</div>
                    %endif
                    
                </div>
            </div>

            <div class="act_as_tbody">
                %for account_at in lines_data:
                    <%
                    current_account = account_at['current']
                    level = current_account['level']
                    %>
                    %if level:  ## how to manage levels?
                    <%
                        styles = []
                        if level < 3:
                            styles.append('font-weight: bold;')
                        else:
                            styles.append('font-weight: normal;')

                        #if level_italic(data, level):
                        #    styles.append('font-style: italic;')
                        #else:
                        #    styles.append('font-style: normal;')

                        #if level_underline(data, level):
                        #    styles.append('text-decoration: underline;')
                        #else:
                        #    styles.append('text-decoration: none;')

                        #if level_uppercase(data, level):
                        #    styles.append('text-transform: uppercase;')
                        #else:
                         #   styles.append('font-decoration: none;')

                        #styles.append("font-size: %spx;" % (level_size(data, level),))

                    %>
                        <div class="act_as_row lines ${"account_level_%s" % (current_account['level'])}" styles="${' '.join(styles)}">
                            ## account name
                            <div class="act_as_cell" style="padding-left: ${current_account['level'] * 5}px; ${' '.join(styles)}">${current_account.name}</div>
                            %if debit_credit:
                                
                                ## debit
                                <div class="act_as_cell amount" style="${' '.join(styles)}">${formatLang(current_account['debit']) | amount}</div>
                                ## credit
                                <div class="act_as_cell amount" style="${' '.join(styles)}">${formatLang(current_account['credit'] * -1) if current_account['credit'] else 0.0 | amount}</div>
                            %endif
                            ## balance
                            <div class="act_as_cell amount" style="${' '.join(styles)}">${formatLang(account_at['balance']) | amount}</div>
                            %if enable_filter:
                                <div class="act_as_cell amount" style="${' '.join(styles)}">${formatLang(account_at['balance_cmp']) | amount}</div>
                            %endif
                            
                        </div>
                    %endif
                %endfor
            </div>
        </div>
    </body>
</html>
