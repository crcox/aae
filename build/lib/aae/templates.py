network = """
addNet ${name} -i ${intervals} -t ${ticksPerInterval} ${netType}

% for GROUP in layers:
    ${add_group(GROUP)}
% endfor

% for CONNECTION in connections:
    ${add_connection(CONNECTION)}
% endfor

<%def name="add_group(GROUP)">
<%
    line = ['addGroup',GROUP['name'],GROUP['nunits']]
    if GROUP['type'] in ['INPUT','OUTPUT']:
        line.append(GROUP['type'])
    if GROUP['type'] in ['HIDDEN','OUTPUT']:
        if GROUP['biased']:
            line.append('BIASED')
        else:
            line.append('-BIASED')
    if GROUP['type'] == 'OUTPUT':
        line.append(GROUP['errorType'])
        line.append(GROUP['criterion'])
%>
    ${' '.join(line)}
</%def>

<%def name="add_connection(CONNECTION)">
<%
    line = ['connectGroups',CONNECTION['pattern'][0],CONNECTION['pattern'][1]]
    line.extend(['-projection',CONNECTION['projection'])
    if 'mean' in CONNECTION['weights'] and CONNECTION['weights']['mean']:
        line.extend('-mean',CONNECTION['weights']['mean']
    else:
        line.extend(['-mean',0])

    if 'range' in CONNECTION['weights']:
        line.extend(['-range',CONNECTION['weights']['range']
    else:
        line.extend(['-range',1])

    if 'bidirectional' in CONNECTION['weights'] and CONNECTION['weights']['bidirectional']:
        line.append('-bidirectional')

    ${' '.join(line)}
%>
</%def>
"""
