import argparse
import os
import json

# from pybquiz import PybQuiz
# from pybquiz.export.pptx import PptxFactory
# from pybquiz.background import BackgroundManager
# from pybquiz.export.googleslide import GoogleSlideFactory, GoogleSheetFactory
from pybquiz.generator.terminal import GeneratorTerminal
from pybquiz.generator.base import QGeneratorTrivia, QGeneratorWWTBAM

from pybquiz.db.base import UnifiedTSVDB
from pybquiz.db.wwtbam import WWTBAM

def main(args):

    # Get input information
    dump_file = args.dump
    dirout = args.dirout
    
    # Assist quiz creation
    if dump_file is None:
        
        # Build DB
        trivia = UnifiedTSVDB()
        wwtbam_us_db = WWTBAM(lang='us')
        wwtbam_uk_db = WWTBAM(lang='uk')
        
        # Build databases generators
        gen_triviadb = QGeneratorTrivia(trivia=trivia)
        gen_wwtbam = QGeneratorWWTBAM(wwtbams=[wwtbam_us_db, wwtbam_uk_db])
    
        # Generate terminal
        dump_file = GeneratorTerminal(
            dirout = dirout,
            dbs = [gen_triviadb, gen_wwtbam]
        ).run_terminal()

    # Check file
    if not os.path.exists(dump_file):
        print("File not found: {}".format(dump_file))
        raise FileNotFoundError
    
    # # Create output directory
    # os.makedirs(args.dirout, exist_ok=True)
    
    # # Save to json
    # name = os.path.splitext(os.path.basename(cfg_yml))[0]
    # outfile_json = os.path.join(args.dirout, "{}.json".format(name))
    # # outfile_pptx = os.path.join(args.dirout, "{}.pptx".format(name))
            
    # # Create quiz
    # if not os.path.exists(outfile_json):
    #     print("Quiz {} does not exists, create it ...".format(name))
    #     quiz = PybQuiz.from_yaml(yaml_path=cfg_yml, yaml_token=token_path)
    #     quiz.dump(file=outfile_json) 
        
    # Create background handler                
    # background_gen = BackgroundManager(dirout=args.dirout)
    
    # Reload from json
    # pptx = PptxFactory()
    # pptx.export(dump_path=outfile_json, outfile=outfile_pptx, background_gen=background_gen)

    # # Check if google slide available
    # if os.path.exists(args.googlecreds):
        
    #     # Create spread sheet
    #     gxls = GoogleSheetFactory(name=name, crendential_file=args.googlecreds)
    #     url_sheet, spreadsheet_id, chart_id = gxls.export(dump_path=outfile_json)

    #     gpptx = GoogleSlideFactory(name=name, crendential_file=args.googlecreds)
    #     url_slide = gpptx.export(dump_path=outfile_json, background_gen=background_gen, spreadsheet_id=spreadsheet_id, sheet_chart_id=chart_id)
        
    #     print("Spreadsheet availble: {}".format(url_sheet))
    #     print("Presentation availble: {}".format(url_slide))

        
if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='pybQuiz Creator',
        description='PybQuiz is a Python package designed to help you create and manage pub quizzes effortlessly',
    )
    parser.add_argument('--dump', default=None,
                        help='path to dump file (default if None)')
    parser.add_argument('--dirout', default="output", 
                        help='path to output directory for data generation (default is "output")')
    parser.add_argument('--googlecreds', default='config/credentials.json', 
                        help='path to stored Google credentials (default is "config/credentials.json")')
    args = parser.parse_args()
    
    main(args=args)
    