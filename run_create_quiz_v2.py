import argparse
import os


from pybquiz.db.base import UnifiedTSVDB
from pybquiz.db.wwtbam import WWTBAM
from pybquiz.generator.terminal import GeneratorTerminal
from pybquiz.generator.trivia import QGeneratorTrivia
from pybquiz.generator.wwtbam import QGeneratorWWTBAM
from pybquiz.export.pptxexport import PPTXExport
from pybquiz.export.googleexport import GoogleExport

def main(args):

    # Get input information
    dump_file = args.dump
    dirout = args.dirout
    
    # Assist quiz creation
    if dump_file is None:
        
        # Build DB
        trivia = UnifiedTSVDB()
        wwtbam = WWTBAM()
        
        # Build databases generators
        gen_triviadb = QGeneratorTrivia(trivia=trivia)
        gen_wwtbam = QGeneratorWWTBAM(wwtbam=wwtbam)
    
        # Check prompt
        prompts = args.prompts
        if prompts is not None:
            prompts = prompts.split("|")
        
        # Generate terminal
        dump_file = GeneratorTerminal(
            dirout = dirout,
            dbs = [gen_triviadb, gen_wwtbam]
        ).run_terminal(
            prompts=prompts
        )
        
    # Check file
    if not os.path.exists(dump_file):
        print("File not found: {}".format(dump_file))
        raise FileNotFoundError

    # Reload from json
    PPTXExport(
        dump_file,
        dirout=args.dirout,
    ).export()
    
    # GoogleExport(
    #     dump_file,
    #     crendential_file=args.googlecreds,
    #     dirout=args.dirout,
    # ).export()
        
    # Create spread sheet
    # gxls = GoogleSheetFactory(name=name, crendential_file=args.googlecreds)
    # url_sheet, spreadsheet_id, chart_id = gxls.export(dump_path=outfile_json)
    # print("Spreadsheet availble: {}".format(url_sheet))

        
if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='PybQuiz is a Python package designed to help you create and manage pub quizzes effortlessly',
    )
    parser.add_argument('--dump', default=None,
                        help='path to dump file (default is None)')
    parser.add_argument('--prompts', 
                        # default="sdsdsd|sdsdsdsdssd|1|A-2-10-HEK", 
                        default="sdsdsd|sdsdsdsdssd|1|B-0-10-EMHK", 
                        # default=None,
                        help='Manual prompts (default is None)')
    parser.add_argument('--dirout', default="output", 
                        help='path to output directory for data generation (default is "output")')
    parser.add_argument('--googlecreds', default='credentials.json', 
                        help='path to stored Google credentials (default is "credentials.json")')
    args = parser.parse_args()
    
    main(args=args)
    
