#
#    Functions for evaluating (and debugging) automatic verb frame and semantic 
#   role detection performance. 
#

from typing import List

import re
import warnings

from collections import OrderedDict

def extract_gold_propbank_frames_from_sentence_conll( sentence_conll: 'Layer', 
                                                      discard_frames_wo_args=True, 
                                                      discard_args_w_illegal_num=True, 
                                                      verbose=True ):
    '''Extracts (gold) frame and semantic role annotations from misc field of a sentence conll syntax layer.
       Each frame will obtain a dict structure:
            {'verb':            ... , 
             'verb_lemma':      ... , 
             'verb_annotation': ... , 
             'verb_base_span':  ... , 
             'args': [ {'arg':      ..., 
                        'base_span': ...,
                        'annotation': ... }, 
                       {'arg':      ..., 
                        'base_span': ...,
                        'annotation': ... }, 
                        ... ]
            }
       Returns (frames:List[Any], discarded_frames:int, discarded_arguments:int).
       
       Parameter `discard_frames_wo_args` specifies whether frames without any arguments will be 
       discarded. Default: True.
       
       Parameter `discard_args_w_illegal_num` specifies whether arguments with illegal numbering 
       (i.e. arg number is not from `['0', '1', '2', '3', '4', '5']`) will be discarded. 
       Default: True.
       
       Parameter `verbose` specifies whether warnings will be printed in case of malformed frame 
       or argument annotations. Default: True.
    '''
    frames = []
    discarded_frames = 0
    discarded_arguments = 0
    # First pass: collect all verb frames
    for word in sentence_conll:
        annotation = word.annotations[0]
        if annotation['misc'] is not None:
            if 'Verb' in annotation['misc']:
                # Create a new Verb frame
                new_frame = {'verb': annotation['misc']['Verb'],
                             'verb_lemma': re.sub( '_[0-9]+$', '', annotation['misc']['Verb'] ), 
                             'verb_annotation': annotation, 
                             'verb_base_span': annotation.span.base_span, 
                             'args': []}
                frames.append( new_frame )
    # Second pass: collect all verb arguments / semantic roles
    for word in sentence_conll:
        annotation = word.annotations[0]
        if annotation['misc'] is not None:
            if 'Arg' in annotation['misc']:
                arg_raw = annotation['misc']['Arg']
                verb, arg, arg_nr = None, None, None
                arg_raw_parts = arg_raw.split('_')
                if len(arg_raw_parts) == 3:
                    # Valid annotation format: Arg=andma_Arg_3
                    verb, arg, arg_nr = arg_raw_parts
                elif len(arg_raw_parts) == 2:
                    if arg_raw_parts[-1].isdigit():
                        # Malformed annotation:  Arg=sõitma_3
                        verb, arg, arg_nr = arg_raw_parts[0], 'arg', arg_raw_parts[-1]
                    elif re.match('Arg[0-9]+', arg_raw_parts[-1]):
                        # Malformed annotation:  Arg=saama_Arg5
                        verb, arg, arg_nr = arg_raw_parts[0], 'arg', arg_raw_parts[-1][-1]
                    else:
                        # Malformed annotation
                        discarded_arguments += 1
                        if verbose:
                            warnings.warn(f'(!) Unable to find verb frame annotation for {annotation.text}:Arg={arg_raw!r} in {sentence_conll.enclosing_text!r}. '+\
                                           'Discarding argument.')
                else:
                    # Malformed annotation:  Arg=1
                    discarded_arguments += 1
                    if verbose:
                        warnings.warn(f'(!) Unable to find verb frame annotation for {annotation.text}:Arg={arg_raw!r} in {sentence_conll.enclosing_text!r}. '+\
                                       'Discarding argument.')
                if verb is not None and arg_nr is not None:
                    arg_num_check_passed = True
                    if discard_args_w_illegal_num:
                        # Check argument number, remove illegal numbers, e.g.
                        #   Arg=andma_Arg_8
                        #   Arg=jääma_Arg_3l
                        #   Arg=leidma_Arg_3t
                        if len(arg_nr) == 0 or \
                           (arg_nr[-1].isdigit() and arg_nr[-1] not in ['0', '1', '2', '3', '4', '5']) or \
                           (arg_nr[-1].isalpha() and len(arg_nr) > 1 and arg_nr[-2].isdigit()):
                            arg_num_check_passed = False
                    if arg_num_check_passed:
                        # Find corresponding verb
                        frames_found = []
                        for frame in frames:
                            if frame['verb_lemma'] == verb:
                                frames_found.append( frame )
                        if len(frames_found) == 0:
                            discarded_arguments += 1
                            if verbose:
                                warnings.warn(f'(!) Unable to find verb frame annotation for {annotation.text}:Arg={arg_raw!r} in {sentence_conll.enclosing_text!r}. '+\
                                               'Discarding argument.')
                        elif len(frames_found) > 1:
                            # There is more than one verb (frame) for the given argument
                            # Try to find verb frame that is parent of the current frame
                            parent_span = annotation['parent_span'].base_span if annotation['parent_span'] is not None else None
                            parent_found = False
                            if parent_span is not None:
                                for frame in frames_found:
                                    verb_base_span = frame['verb_base_span']
                                    if verb_base_span == parent_span:
                                        frame['args'].append( {'arg': f'{arg.lower()}{arg_nr}', \
                                                               'base_span': annotation.span.base_span,
                                                               'annotation': annotation } )
                                        parent_found = True
                                        break
                            if not parent_found:
                                discarded_arguments += 1
                                if verbose:
                                    warnings.warn(f'(!) More than one verb frame annotations for {annotation.text}:Arg={arg_raw!r} in {sentence_conll.enclosing_text!r}: \n'+\
                                                  f'{frames_found!r}. Discarding argument.')
                        else:
                            frames_found[0]['args'].append( {'arg': f'{arg.lower()}{arg_nr}', \
                                                             'base_span': annotation.span.base_span,
                                                             'annotation': annotation } )
                    else:
                        discarded_arguments += 1
                        if verbose:
                            warnings.warn(f'(!) Illegal argument numbering in {annotation.text}:Arg={arg_raw!r} in {sentence_conll.enclosing_text!r}. '+\
                                           'Discarding argument.')
    # Discard verb frames without any argument 
    if discard_frames_wo_args:
        to_delete = []
        for frame in frames:
            if len(frame['args']) == 0:
                annotation = frame['verb_annotation']
                verb_with_sense = frame['verb']
                if verbose:
                    warnings.warn(f'(!) No arguments found for verb {annotation.text}:{verb_with_sense} in {sentence_conll.enclosing_text!r}. '+\
                                   'Discarding the frame.')
                    discarded_frames += 1
                to_delete.append(frame)
        for df in to_delete:
            frames.remove(df)
    return frames, discarded_frames, discarded_arguments


def _extract_comparable_info_from_auto_frame( auto_frame: 'Relation' ):
    '''Extracts frame and semantic role annotations from automatically created Relation annotation. 
       Returns (verb_base_span, verb_with_sense, [('arg0', base_spans), ..., ('argm_loc', base_spans)] )
    '''
    auto_verb_base_span = auto_frame.verb.base_span[0]
    auto_verb_with_sense = auto_frame.annotations[0]['sense_id']
    if not auto_verb_with_sense[-1].isdigit():
        # If verb does not end with sense number, add sense number '_1'
        auto_verb_with_sense += '_1'
    auto_arg_base_spans = []
    for argn in ['arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'argm_mnr', 'argm_tmp', 'argm_loc']:
        if argn in auto_frame.span_names:
            named_span = auto_frame[argn]
            assert named_span is not None
            base_spans = named_span.base_span
            auto_arg_base_spans.append( (argn, base_spans) )
    return auto_verb_base_span, auto_verb_with_sense, auto_arg_base_spans


def get_gold_frame_verbs( sent_text_objects: List['Text'], syntax_layer='conll_syntax', 
                          discard_frames_wo_args=True, discard_args_w_illegal_num=True ):
    '''Extracts all verbs (verb lemmas) triggering frames from the given list of (gold) sentence conll syntax layers.
       Returns set of verb lemmas.
    '''
    verbs_set = set()
    for sent_text in sent_text_objects:
        gold_frames, discarded_frames, discarded_arguments = \
            extract_gold_propbank_frames_from_sentence_conll( sent_text[syntax_layer], \
                                                              discard_frames_wo_args=discard_frames_wo_args, \
                                                              discard_args_w_illegal_num=discard_args_w_illegal_num, \
                                                              verbose=False )
        for gold_frame in gold_frames:
            verbs_set.add( gold_frame['verb_lemma'] )
    return verbs_set


def eval_propbank_preannotator_on_sentence_conll( sentence_conll: 'Layer', auto_semantic_roles: 'RelationLayer', results: dict, 
                                                  target_verbs: set = None, 
                                                  discard_frames_wo_args=True, 
                                                  discard_args_w_illegal_num=True, 
                                                  verbose=False ):
    '''Evaluates semantic role annotation on a single sentence and saves evaluation statistics/counts into results dict. 
       
       Parameter `sentence_conll` is a Layer with gold standard conllu syntax annotations from which gold standard frames 
       will be retrieved. 
       
       Parameter `auto_semantic_roles` holds a RelationLayer with automatically produced frame annotations of the given 
       sentence. This is the target of evaluation. 
       
       Parameter `results` is a dictionary where evaluation results will be recorded. 
       
       Parameter `target_verbs` can be a set of verb lemmas for focusing evaluation only on given verbs. 
       If not set (default), then evaluation will cover all verbs in gold standard and auto annotations. 
       
       Parameter `discard_frames_wo_args` specifies whether gold standard frames without any arguments will 
       be discarded. Default: True.
       
       Parameter `discard_args_w_illegal_num` specifies whether gold standard arguments with illegal numbering 
       (i.e. arg number is not from `['0', '1', '2', '3', '4', '5']`) will be discarded. Default: True.
       
    '''
    assert auto_semantic_roles.enveloping == sentence_conll.name
    gold_frames, discarded_frames, discarded_arguments = \
        extract_gold_propbank_frames_from_sentence_conll( sentence_conll, \
                                                          discard_frames_wo_args=discard_frames_wo_args, \
                                                          discard_args_w_illegal_num=discard_args_w_illegal_num, \
                                                          verbose=verbose )
    results['discarded_gold_frames'] = results.setdefault('discarded_gold_frames', 0) + discarded_frames
    results['discarded_gold_args'] = results.setdefault('discarded_gold_args', 0) + discarded_arguments
    all_matching_auto_frames = set()
    for gold_frame in gold_frames:
        # Skip verbs that are not evaluation target
        if target_verbs is not None and gold_frame['verb_lemma'] not in target_verbs:
            continue
        # Get gold verb and args
        verb_with_sense = gold_frame['verb']
        results['frame_gold_total'] = results.setdefault('frame_gold_total', 0) + 1
        if not verb_with_sense[-1].isdigit():
            # If verb does not end with sense number, add sense number '_1'
            verb_with_sense += '_1'
        verb_base_span = gold_frame['verb_base_span']
        gold_arg_base_spans = \
            [ (gold_arg['arg'], gold_arg['base_span']) for gold_arg in gold_frame['args'] ]
        # Get matching auto frames 
        # (note: due to ambiguity, there can be more than one frame per verb)
        matching_auto_frames = []
        for fid, auto_frame in enumerate(auto_semantic_roles):
            if auto_frame.verb is not None:
                auto_verb_base_span = auto_frame.verb.base_span[0]
                if auto_verb_base_span == verb_base_span:
                    # Extract comparable information
                    auto_verb_base_span, auto_verb_sense, auto_arg_base_spans = \
                            _extract_comparable_info_from_auto_frame( auto_frame )
                    matching_auto_frames.append( (fid,
                                                  auto_verb_base_span, 
                                                  auto_verb_sense, 
                                                  auto_arg_base_spans) )
                    all_matching_auto_frames.add( fid )
        # 1) Evaluate auto frame that has a matching sense
        sense_matching_auto_fid = None
        full_matching_auto_fid = None
        for fid, (_, auto_verb_span, auto_verb_sense, auto_arg_spans) in enumerate(matching_auto_frames):
            if auto_verb_sense == verb_with_sense:
                # Sense of the auto frame matches that of the golden frame
                sense_matching_auto_fid = fid
                results['frame_verb_sense_match'] = results.setdefault('frame_verb_sense_match', 0) + 1
                # Compare arguments
                auto_arg_match = set()
                for gold_arg, gold_span in gold_arg_base_spans:
                    results['arg_gold_total'] = \
                        results.setdefault( 'arg_gold_total', 0 ) + 1
                    results[f'{gold_arg}_gold_total'] = \
                        results.setdefault( f'{gold_arg}_gold_total', 0 ) + 1
                    label_found = False
                    span_found = False
                    for (argn, base_spans) in auto_arg_spans:
                        if gold_arg == argn:
                            label_found = True
                            contains_gold_span = False
                            for auto_spn in base_spans:
                                if auto_spn == gold_span:
                                    contains_gold_span = True
                                    break
                            if contains_gold_span:
                                span_found = True
                                auto_arg_match.add( argn )
                                results['arg_match'] = \
                                    results.setdefault( 'arg_match', 0 ) + 1
                                results[f'{gold_arg}_match'] = \
                                    results.setdefault( f'{gold_arg}_match', 0 ) + 1
                                if len(base_spans) > 1:
                                    results['arg_match_extra'] = \
                                        results.setdefault('arg_match_extra', 0) + len(base_spans)-1
                                    results[f'{gold_arg}_match_extra'] = \
                                        results.setdefault(f'{gold_arg}_match_extra', 0) + len(base_spans)-1
                    if not span_found:
                        results['arg_missing'] = \
                            results.setdefault( 'arg_missing', 0 ) + 1
                        results[f'{gold_arg}_missing'] = \
                            results.setdefault( f'{gold_arg}_missing', 0 ) + 1
                # Redundant auto spans (no match with any gold_arg span)
                for (argn, base_spans) in auto_arg_spans:
                    if argn not in auto_arg_match:
                        results['arg_redundant'] = \
                            results.setdefault( 'arg_redundant', 0 ) + 1
                        results[f'{argn}_redundant'] = \
                            results.setdefault( f'{argn}_redundant', 0 ) + 1
                # Record full match
                if len(auto_arg_match) == len(auto_arg_spans) and len(auto_arg_match) == len(gold_arg_base_spans):
                    results['frame_full_match'] = results.setdefault('frame_full_match', 0) + 1
                    full_matching_auto_fid = fid
            else:
                # This was a redundant auto frame (verb location is correct, but sense is wrong)
                results['frame_verb_sense_redundant'] = results.setdefault('frame_verb_sense_redundant', 0) + 1
        if sense_matching_auto_fid is not None and len(matching_auto_frames) > 1:
            # Check whether redundant frames are totally consumed by a matching frame
            for fid, (_, auto_verb_span, auto_verb_sense, auto_arg_spans) in enumerate(matching_auto_frames):
                if fid != sense_matching_auto_fid  and  fid != full_matching_auto_fid:
                    sense_matching_frame = matching_auto_frames[sense_matching_auto_fid]
                    if auto_verb_span == sense_matching_frame[1]:
                        # Check whether all arg spans of a redundant frame are contained 
                        # within a (partially) matching frame
                        contained = 0
                        for (red_argn, red_base_spans) in auto_arg_spans:
                            for (match_argn, match_base_spans) in sense_matching_frame[-1]:
                                if red_argn == match_argn  and  red_base_spans == match_base_spans:
                                    contained += 1
                        if contained == len(auto_arg_spans):
                            results['frame_verb_sense_redundant_contained_sense_match'] = \
                                results.setdefault('frame_verb_sense_redundant_contained_sense_match', 0) + 1
                    if full_matching_auto_fid is not None:
                        full_matching_frame = matching_auto_frames[full_matching_auto_fid]
                        if auto_verb_span == full_matching_frame[1]:
                            # Check whether all arg spans of a redundant frame are contained 
                            # within a (partially) matching frame
                            contained = 0
                            for (red_argn, red_base_spans) in auto_arg_spans:
                                for (match_argn, match_base_spans) in full_matching_frame[-1]:
                                    if red_argn == match_argn  and  red_base_spans == match_base_spans:
                                        contained += 1
                            if contained == len(auto_arg_spans):
                                results['frame_verb_sense_redundant_contained_full_match'] = \
                                    results.setdefault('frame_verb_sense_redundant_contained_full_match', 0) + 1
        if sense_matching_auto_fid is None and full_matching_auto_fid is None:
            # A missing frame: has no matching auto frames found
            results['frame_missing'] = results.setdefault('frame_missing', 0) + 1
    # Check for totally redundant frames (no matching verb lemma in gold standard)
    for fid, auto_frame in enumerate( auto_semantic_roles ):
        verb_lemma = re.sub( '_[0-9]+$', '', auto_frame.annotations[0]['sense_id'] )
        # Skip verbs that are not evaluation target
        if target_verbs is not None and verb_lemma not in target_verbs:
            continue
        results['frame_auto_total'] = results.setdefault('frame_auto_total', 0) + 1
        if fid not in all_matching_auto_frames:
            # This was a redundant auto frame
            results['frame_redundant'] = results.setdefault('frame_redundant', 0) + 1
    results['sentences'] = results.setdefault('sentences', 0) + 1



def summarize_eval_accuracies( eval_results: dict, return_dataframes: bool=False ):
    '''Calculates frame and argument detection accuracies from eval_results.
       
       Parameter `return_dataframes` is set, then frame and argument results will 
       be converted from dicts to dataframes. 
       
       Returns frame_results, arg_results.
    '''
    # Results on frame annotation
    discarded_gold_frames = eval_results.get('discarded_gold_frames', 0)
    frame_auto_total      = eval_results.get('frame_auto_total', 0)
    frame_gold_total      = eval_results.get('frame_gold_total', 0)
    frame_missing         = eval_results.get('frame_missing', 0)
    frame_redundant       = eval_results.get('frame_redundant', 0)
    frame_full_match      = eval_results.get('frame_full_match', 0)
    frame_sense_match     = eval_results.get('frame_verb_sense_match', 0)
    frame_sense_redundant = eval_results.get('frame_verb_sense_redundant', 0)
    frame_results = OrderedDict()
    if frame_gold_total > 0:
        frame_results['full match accuracy']  = f'{(frame_full_match/frame_gold_total*100.0):.2f}'
        frame_results['sense match accuracy'] = f'{(frame_sense_match/frame_gold_total*100.0):.2f}'
    else:
        frame_results['full match accuracy'] = f'N/A'
        frame_results['sense match accuracy'] = f'N/A'
    if frame_auto_total > 0:
        frame_results['redundant senses %'] = f'{(frame_sense_redundant/frame_auto_total*100.0):.2f}%'
        frame_results['redundant frames %'] = f'{(frame_redundant/frame_auto_total*100.0):.2f}%'
    else:
        frame_results['redundant senses %'] = f'N/A'
        frame_results['redundant frames %'] = f'N/A'
    if frame_gold_total > 0:
        frame_results['missing frames %'] = f'{(frame_missing/frame_gold_total*100.0):.2f}%'
    else:
        frame_results['missing frames %'] = f'N/A'
    frame_results['fully matching'] = frame_full_match
    frame_results['sense matching'] = frame_sense_match
    frame_results['redundant senses'] = frame_sense_redundant
    frame_results['redundant frames'] = frame_redundant
    frame_results['missing frames']   = frame_missing
    frame_results['total gold frames'] = frame_gold_total
    frame_results['total auto frames'] = frame_auto_total
    frame_results['discarded gold frames'] = discarded_gold_frames
    discarded_gold_args = eval_results.get('discarded_gold_args', 0)
    frame_results['discarded gold args'] = discarded_gold_args
    # Convert all values to lists (for visualization with pandas)
    for k,v in frame_results.items():
        frame_results[k] = [v]
    # Results on arg annotation
    arg_results = OrderedDict()
    arg_results['rows'] = ['accuracy', 'matching', 'missing', 'redundant', 'total gold']
    for arg_name in ['arg', 'arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5']:
        col_name = arg_name.upper()
        if col_name == 'ARG':
            col_name = 'ARG_OVERALL'
        arg_gold_total = eval_results.get(f'{arg_name}_gold_total', 0)
        arg_missing    = eval_results.get(f'{arg_name}_missing', 0)
        arg_redundant  = eval_results.get(f'{arg_name}_redundant', 0)
        arg_match      = eval_results.get(f'{arg_name}_match', 0)
        arg_match_xtra = eval_results.get(f'{arg_name}_match_extra', 0)
        if arg_gold_total > 0:
            arg_results[col_name] = [f'{(arg_match/arg_gold_total*100.0):.2f}']
        else:
            arg_results[col_name] = [f'N/A']
        arg_results[col_name].append(arg_match)
        arg_results[col_name].append(arg_missing)
        arg_results[col_name].append(arg_redundant)
        arg_results[col_name].append(arg_gold_total)
    if not return_dataframes:
        return frame_results, arg_results
    else:
        import pandas as pd
        return pd.DataFrame.from_dict(frame_results, orient='columns'), \
               pd.DataFrame.from_dict(arg_results, orient='columns')

