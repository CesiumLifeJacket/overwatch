from cgi import escape
import jinja2

# TODO: create function which takes file path and errors and generates HTML page
# TOOD: return html as a string, or write it to a file somewhere?

template = jinja2.Template(open('web-template/file.html').read())

def annotate_code(code, violations):
    violations = iter(sorted(violations, key=lambda v: (v['row'], v['col']) ))

    insertions = set() # (index, "text-to-insert") pairs.
    col = 1
    line = 1
    last_i = 0
    violation = next(violations)

    # Produce spans and where to insert them

    for index, char in enumerate(code):
        
        if line == violation['row'] and col == violation['col']:
            
            # span tags
            span_start = '<span class="violation" title="{}">'.format(
                escape(violation['message'])
                )
            span_end = '</span>'

            # index where the span ends
            end_index = index + violation.get('length', 1)

            # queue these up for insertion
            insertions.add((index, span_start))
            insertions.add((end_index, span_end))

            # get the next violation
            try:
                violation = next(violations)
            except StopIteration:
                break

        if char == '\n':
            line += 1
            col = 1
        else:
            col += 1

    # Insert the spans

    segments = []
    prev_index = 0
    for index, text in sorted(insertions):

        # add the code itself, with HTML special chars escaped
        segments.append(escape(code[prev_index:index]))

        # add the annotation (span)
        segments.append(text)

        # move the previous index up
        prev_index = index

    # Wdd the remaining text
    segments.append(escape(code[prev_index:]))

    # Join all the segments together into the final product
    annotated_code = ''.join(segments)

    return annotated_code

def generate(language, code, violations):
    annotated_code = annotate_code(code, violations)
    return template.render(language=language, code=annotated_code)
