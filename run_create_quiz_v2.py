import argparse
import os
import json

# from pybquiz import PybQuiz
from pybquiz.export.pptx import PptxFactory
from pybquiz.export.pptxexport import PPTXExport

from pybquiz.background import BackgroundManager
# from pybquiz.export.googleslide import GoogleSlideFactory, GoogleSheetFactory
from pybquiz.generator.terminal import GeneratorTerminal
from pybquiz.generator.base import QGeneratorTrivia, QGeneratorWWTBAM

from pybquiz.export.base import Export
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

    # Reload from json
    PPTXExport(
        dump_file,
        dirout=args.dirout,
    ).export()
    
    # outfile_pptx = os.path.splitext(dump_file)[0] + ".pptx"
    # pptx = PptxFactory()
    # pptx.export(
    #     dump_path=dump_file, 
    #     outfile=outfile_pptx, 
    #     background_gen=background_gen
    # )

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
    