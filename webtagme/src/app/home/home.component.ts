import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders} from '@angular/common/http';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  constructor(private http: HttpClient) { }

  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type':  'application/x-www-form-urlencoded'
    })
  };

  // tslint:disable-next-line:max-line-length
  tagmeText = 'Diffuse intrinsic pontine glioma (or DIPG) are pediatric high-grade gliomas associated with a dismal prognosis. They harbor specific substitution in histone H3 at position K27 that induces major epigenetic dysregulations. Most clinical trials failed so far to increase survival, and radiotherapy remains the most efficient treatment, despite only transient tumor control. We conducted the first lentiviral shRNA dropout screen in newly diagnosed DIPG to generate a cancer-lethal signature as a basis for the development of specific treatments with increased efficacy and reduced side effects compared to existing anticancer therapies. The analysis uncovered 41 DIPG essential genes among the 672 genes of human kinases tested, for which several distinct interfering RNAs impaired cell expansion of three different DIPG stem-cell cultures without deleterious effect on two control neural stem cells. Among them, PLK1, AURKB, CHEK1, EGFR, and GSK3A were previously identified by similar approach in adult GBM indicating common dependencies of these cancer cells and pediatric gliomas. As expected, we observed an enrichment of genes involved in proliferation and cell death processes with a significant number of candidates belonging to PTEN/PI3K/AKT and EGFR pathways already under scrutiny in clinical trials in this disease. We highlighted VRK3, a gene involved especially in cell cycle regulation, DNA repair, and neuronal differentiation, as a non-oncogenic addiction in DIPG. Its repression totally blocked DIPG cell growth in the four cellular models evaluated, and induced cell death in H3.3-K27M cells specifically but not in H3.1-K27M cells, supporting VRK3 as an interesting and promising target in DIPG.';
  result = [];

  ngOnInit() {
  }

  tagme() {

    const apiUrl = 'http://161.97.160.81/tagme_string';
    const parameters = 'name=' + encodeURIComponent(this.tagmeText);

    this.http.post(apiUrl, parameters, this.httpOptions).subscribe((data) => {
      console.log(data['response']);
      this.result = data['response'];
    });
  }

}
